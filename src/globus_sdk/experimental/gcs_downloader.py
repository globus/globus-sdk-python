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
import globus_sdk.scopes
import globus_sdk.transport
from globus_sdk._internal.classprop import classproperty
from globus_sdk._internal.type_definitions import Closable
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.transport.default_retry_checks import DEFAULT_RETRY_CHECKS

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

log = logging.getLogger(__name__)


class HTTPSClientConstructor(t.Protocol):
    """A protocol which defines the factory type used to customize a GCSDownloader."""

    def __call__(
        self,
        *,
        collection_client_id: str,
        default_scope_requirements: t.Iterable[globus_sdk.Scope],
        base_url: str,
    ) -> GCSCollectionHTTPSClient: ...


class GCSDownloader:
    """
    An object which manages connection and authentication state to enable HTTPS
    downloads from a specific Globus Connect Server.

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
    :param https_client: The underlying client used for the file read request. Typically
        omitted. When not provided, one will be constructed on demand by the downloader.
        As an alternative to providing a client, a callable factory may be passed here,
        which will be given the ``collection_client_id``,
        ``default_scope_requirements``, and ``base_url`` and must return a new client.
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
        https_client: GCSCollectionHTTPSClient | HTTPSClientConstructor | None = None,
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

        # three essential cases for https_client:
        # 1. default, setup the default client factory method
        if https_client is None:
            self.https_client: GCSCollectionHTTPSClient | None = None
            self._https_client_constructor: HTTPSClientConstructor = (
                self._default_https_client_constructor
            )
        # 2. concrete client, store (default factory is set for type safety, but will
        #    not be used)
        elif isinstance(https_client, GCSCollectionHTTPSClient):
            self.https_client = https_client
            self._https_client_constructor = self._default_https_client_constructor
        # 3. factory method, store it and no client
        else:
            self.https_client = None
            self._https_client_constructor = https_client

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
        if self.https_client is None:
            self.https_client = self._get_client_from_uri(file_uri)
            self._resources_to_close.append(self.https_client)

        response = self.https_client.get(file_uri)
        if as_text:
            return response.text
        return response.binary_content

    def _get_client_from_uri(self, file_uri: str) -> GCSCollectionHTTPSClient:
        collection_id = self._sniff_collection_id(file_uri)
        scopes = self._detect_scopes(collection_id)
        base_url = _get_base_url(file_uri)
        return self._https_client_constructor(
            collection_client_id=collection_id,
            default_scope_requirements=scopes,
            base_url=base_url,
        )

    def _default_https_client_constructor(
        self,
        *,
        collection_client_id: str,
        default_scope_requirements: t.Iterable[globus_sdk.Scope],
        base_url: str,
    ) -> GCSCollectionHTTPSClient:
        return GCSCollectionHTTPSClient(
            collection_client_id,
            default_scope_requirements,
            app=self.app,
            base_url=base_url,
            transport=self.transport,
        )

    def _detect_scopes(self, collection_id: str) -> list[globus_sdk.Scope]:
        if self.transfer_client is None:
            self.transfer_client = globus_sdk.TransferClient(
                app=self.app, transport=self.transport
            )
            self._resources_to_close.append(self.transfer_client)
        scopes = globus_sdk.scopes.GCSCollectionScopes(collection_id)
        if _uses_data_access(self.transfer_client, collection_id):
            return [scopes.https, scopes.data_access]
        return [scopes.https]

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


class GCSCollectionHTTPSClient(globus_sdk.BaseClient):
    """
    A dedicated client type for an HTTPS-capable Collection used for file downloads.

    Users should generally not instantiate this class directly, but instead rely on
    :class:`GCSDownloader` to properly initialize these clients.

    .. sdk-sphinx-copy-params:: BaseClient

        :param collection_client_id: The ID of the collection.
        :param default_scope_requirements: The scopes needed for HTTPS access to the
            collection. This should contain the `https` scope for the collection and the
            `data_access` scope if applicable.
    """

    def __init__(
        self,
        collection_client_id: str,
        default_scope_requirements: t.Iterable[globus_sdk.Scope] = (),
        *,
        environment: str | None = None,
        base_url: str | None = None,
        app: globus_sdk.GlobusApp | None = None,
        app_scopes: list[globus_sdk.scopes.Scope] | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport: globus_sdk.transport.RequestsTransport | None = None,
        retry_config: globus_sdk.transport.RetryConfig | None = None,
    ) -> None:
        self.collection_client_id = collection_client_id
        self._default_scope_requirements = list(default_scope_requirements)
        super().__init__(
            environment=environment,
            base_url=base_url,
            app=app,
            app_scopes=app_scopes,
            authorizer=authorizer,
            app_name=app_name,
            transport=transport,
            retry_config=retry_config,
        )

    @classproperty
    def resource_server(  # pylint: disable=missing-param-doc
        self_or_cls: globus_sdk.BaseClient | type[globus_sdk.BaseClient],
    ) -> str | None:
        """
        The resource server for a GCS collection is the ID of the collection.

        This will return None if called as a classmethod as an instantiated
        ``GCSClient`` is required to look up the client ID from the endpoint.
        """
        if not isinstance(self_or_cls, GCSCollectionHTTPSClient):
            return None

        return self_or_cls.collection_client_id

    @property
    def default_scope_requirements(self) -> list[globus_sdk.Scope]:
        return self._default_scope_requirements


def _get_base_url(file_uri: str) -> str:
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
