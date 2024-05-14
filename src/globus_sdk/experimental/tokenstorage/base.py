from __future__ import annotations

import abc
import contextlib
import os
import typing as t

from globus_sdk.services.auth import OAuthTokenResponse

from .token_data import TokenData


class TokenStorage(metaclass=abc.ABCMeta):
    """
    Abstract base class for interacting with an underlying storage system to manage
    storage of token data.

    The ``namespace`` is a user-supplied way of partitioning data, and any token
    response data passed to the storage adapter are stored indexed by
    *resource_server*. If you have a more complex use-case in which this scheme will be
    insufficient, you should encode that in your choice of ``namespace`` values.
    """

    def __init__(self, namespace: str = "DEFAULT") -> None:
        """
        :param namespace: A user-supplied namespace for partitioning token data.
        """
        self.namespace = namespace

    @abc.abstractmethod
    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: dict[str, TokenData]
    ) -> None:
        """
        Store token data in underlying storage partitioned by the resource server
        and the current namespace.

        :param token_data_by_resource_server: a ``dict`` of ``TokenData`` objects
        indexed by their ``resource_server``.
        """

    @abc.abstractmethod
    def get_token_data_by_resource_server(self) -> dict[str, TokenData]:
        """
        Lookup all token data under the current namespace in the underlying storage.

        Returns a dict of ``TokenData`` objects indexed by their resource server.
        """

    def get_token_data(self, resource_server: str) -> TokenData | None:
        """
        Lookup token data for a resource server in the underlying storage
        under the current namespace.

        Either returns a ``TokenData`` object containing tokens and metadata for
        the given resource server or ``None`` indicating that there was no data for
        that resource server.

        :param resource_server: The resource_server string to get token data for
        """
        return self.get_token_data_by_resource_server().get(resource_server)

    @abc.abstractmethod
    def remove_token_data(self, resource_server: str) -> bool:
        """
        Remove all token data for a resource server from the underlying storage under
        the current namespace.

        Returns True if token data was deleted, False if none was found to delete.

        :param resource_server: The resource server string to remove token data for
        """

    def store_token_response(self, token_response: OAuthTokenResponse) -> None:
        """
        Wrapper around ``store_token_data_by_resource_server`` that accepts an
        ``OAuthTokenResponse``.

        :param token_response: An ``OAuthTokenResponse`` from an authentication flow
        """
        token_data_by_resource_server = {}

        # get identity_id from id_token if available
        if token_response.get("id_token"):
            decoded_id_token = token_response.decode_id_token()
            identity_id = decoded_id_token["sub"]
        else:
            identity_id = None

        for resource_server, token_dict in token_response.by_resource_server.items():
            token_data_by_resource_server[resource_server] = TokenData(
                resource_server=token_dict["resource_server"],
                identity_id=identity_id,
                scope=token_dict["scope"],
                access_token=token_dict["access_token"],
                refresh_token=token_dict.get("refresh_token"),
                expires_at_seconds=token_dict["expires_at_seconds"],
                token_type=token_dict.get("token_type"),
            )
        self.store_token_data_by_resource_server(token_data_by_resource_server)


class FileTokenStorage(TokenStorage, metaclass=abc.ABCMeta):
    """
    File adapters are for single-user cases, where we can assume that there's a
    simple file-per-user and users are only ever attempting to read their own
    files.
    """

    filename: str

    def file_exists(self) -> bool:
        """
        Check if the file used by this file storage adapter exists.
        """
        return os.path.exists(self.filename)

    @contextlib.contextmanager
    def user_only_umask(self) -> t.Iterator[None]:
        """
        A context manager to deny rwx to Group and World, x to User

        This does not create a file, but ensures that if a file is created while in the
        context manager, its permissions will be correct on unix systems.

        .. note::

            On Windows, this has no effect. To control the permissions on files used for
            token storage, use ``%LOCALAPPDATA%`` or ``%APPDATA%``.
            These directories should only be accessible to the current user.
        """
        old_umask = os.umask(0o177)
        try:
            yield
        finally:
            os.umask(old_umask)
