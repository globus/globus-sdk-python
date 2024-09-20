from __future__ import annotations

import abc
import contextlib
import os
import typing as t

from globus_sdk.services.auth import OAuthTokenResponse


class StorageAdapter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def store(self, token_response: OAuthTokenResponse) -> None:
        """
        Store an `OAuthTokenResponse` in the underlying storage for this adapter.

        :param token_response: The token response to store
        """

    @abc.abstractmethod
    def get_token_data(self, resource_server: str) -> dict[str, t.Any] | None:
        """
        Lookup token data for a resource server

        Either returns a dict with the access token, refresh token (optional), and
        expiration time, or returns ``None``, indicating that there was no data for that
        resource server.

        :param resource_server: The resource_server string which uniquely identifies the
            token data to retriever from storage
        """

    def on_refresh(self, token_response: OAuthTokenResponse) -> None:
        """
        By default, the on_refresh handler for a token storage adapter simply
        stores the token response.

        :param token_response: The token response received from the refresh
        """
        self.store(token_response)


class FileAdapter(StorageAdapter, metaclass=abc.ABCMeta):
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
