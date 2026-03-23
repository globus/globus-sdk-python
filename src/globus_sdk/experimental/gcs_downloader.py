"""
The GCSDownloader provides HTTPS file download capabilities for Globus Connect Server.
"""

from __future__ import annotations

import logging
import sys
import types
import typing as t
import urllib.parse

import globus_sdk
import globus_sdk.transport
from globus_sdk._internal.type_definitions import Closable
from globus_sdk.experimental.gcs_collection_client import GCSCollectionClient
from globus_sdk.transport.default_retry_checks import DEFAULT_RETRY_CHECKS

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

log = logging.getLogger(__name__)


class GCSDownloader:
    """
    An object which manages connection and authentication state to enable HTTPS
    downloads from a specific Globus Connect Server collection.

    The initial request to read a file features support for determining authentication
    requirements dynamically, and subsequent requests will reuse that authentication
    data.

    Using a single :class:`GCSDownloader` to access distinct collections is not
    supported. A separate downloader should be used for each collection.

    Downloaders may be used as context managers, in which case they automatically call
    their ``close()`` method on exit:

    >>> with GCSDownloader(app) as downloader:
    >>>     print(downloader.read_file(url))

    :param app: The :class:`GlobusApp` used to authenticate calls to this server.
    :param gcs_client: The underlying client used for the file read request. Typically
        omitted. When not provided, one will be constructed on demand by the downloader.
    :param transfer_client: A client used when detecting collection information.
        Typically omitted. When not provided, one will be constructed on demand by the
        downloader.
    :param transport: A transport for the downloader, used for authentication
        sniffing operations. When a client is built by the downloader it will
        inherit this transport.
    """

    def __init__(
        self,
        app: globus_sdk.GlobusApp,
        *,
        gcs_client: GCSCollectionClient | None = None,
        transfer_client: globus_sdk.TransferClient | None = None,
        transport: globus_sdk.transport.RequestsTransport | None = None,
    ) -> None:
        self.app = app
        self._resources_to_close: list[Closable] = []

        if transport is not None:
            self.transport = transport
        else:
            self.transport = globus_sdk.transport.RequestsTransport()
            self._resources_to_close.append(self.transport)

        # the downloader will need a RetryConfig when it uses its own transport
        self._retry_config = globus_sdk.transport.RetryConfig()
        self._retry_config.checks.register_many_checks(DEFAULT_RETRY_CHECKS)

        self.gcs_client = gcs_client

        # set the transfer_client if provided
        self.transfer_client = transfer_client

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """
        Close all resources which are owned by this downloader.
        """
        for resource in self._resources_to_close:
            log.debug(
                f"closing resource of type {type(resource).__name__} "
                f"for {type(self).__name__}"
            )
            resource.close()

    @t.overload
    def read_file(self, file_uri: str, *, as_text: t.Literal[True]) -> str: ...
    @t.overload
    def read_file(self, file_uri: str, *, as_text: t.Literal[False]) -> bytes: ...
    @t.overload
    def read_file(self, file_uri: str) -> str: ...

    def read_file(self, file_uri: str, *, as_text: bool = True) -> str | bytes:
        """
        Given a file URI on a GCS Collection, read the data.

        :param file_uri: The full URI of the file on the collection which is being
            downloaded.
        :param as_text: When ``True``, the file contents are decoded into a string. Set
            to ``False`` to retrieve data as bytes.

        .. caution::

            The file read is done naively as a GET request. This may be unsuitable for
            very large files.
        """
        # dynamically build a client if needed
        if self.gcs_client is None:
            self.gcs_client = self._get_client_from_uri(file_uri)
            self._resources_to_close.append(self.gcs_client)

        response = self.gcs_client.get(file_uri)
        if as_text:
            return response.text
        return response.binary_content

    def _get_client_from_uri(self, file_uri: str) -> GCSCollectionClient:
        collection_id = self._sniff_collection_id(file_uri)
        collection_address = _get_collection_address(file_uri)

        client = self._gcs_client_constructor(
            collection_client_id=collection_id,
            collection_address=collection_address,
        )
        self.app.add_scope_requirements(
            {client.scopes.resource_server: self._determine_required_scopes(client)}
        )
        return client

    def _gcs_client_constructor(
        self, *, collection_client_id: str, collection_address: str
    ) -> GCSCollectionClient:
        return GCSCollectionClient(
            collection_client_id,
            collection_address,
            app=self.app,
            transport=self.transport,
        )

    def _determine_required_scopes(
        self, client: GCSCollectionClient
    ) -> list[globus_sdk.Scope]:
        if self.transfer_client is None:
            self.transfer_client = globus_sdk.TransferClient(
                app=self.app, transport=self.transport
            )
            self._resources_to_close.append(self.transfer_client)

        required_scopes: list[globus_sdk.Scope] = [client.scopes.https]
        if _uses_data_access(self.transfer_client, client.collection_id):
            required_scopes.append(client.scopes.data_access)
        return required_scopes

    def _sniff_collection_id(self, file_uri: str) -> str:
        response = self.transport.request(
            "GET",
            file_uri,
            caller_info=globus_sdk.transport.RequestCallerInfo(
                retry_config=self._retry_config
            ),
            allow_redirects=False,
        )
        if "Location" not in response.headers:
            msg = (
                f"Attempting to detect the collection ID for the file at '{file_uri}' "
                "failed. Did not receive a redirect with Location header on "
                "unauthenticated call."
            )
            raise RuntimeError(msg)

        location_header = response.headers["Location"]
        parsed_location = urllib.parse.urlparse(location_header)
        parsed_location_qs = urllib.parse.parse_qs(parsed_location.query)

        if "client_id" not in parsed_location_qs:
            msg = (
                f"Attempting to detect the collection ID for the file at '{file_uri}' "
                "failed. Location header did not encode a 'client_id'."
            )
            raise RuntimeError(msg)

        client_ids = parsed_location_qs["client_id"]
        if len(client_ids) != 1:
            msg = (
                f"Attempting to detect the collection ID for the file at '{file_uri}' "
                "failed. Multiple 'client_id' params were present."
            )
            raise RuntimeError(msg)

        return client_ids[0]


def _get_collection_address(file_uri: str) -> str:
    parsed = urllib.parse.urlparse(file_uri)
    return f"{parsed.scheme}://{parsed.netloc}"


def _uses_data_access(
    transfer_client: globus_sdk.TransferClient, collection_id: str
) -> bool:
    doc = transfer_client.get_endpoint(collection_id)
    if doc["entity_type"] != "GCSv5_mapped_collection":
        return False
    if doc["high_assurance"]:
        return False
    return True
