from __future__ import annotations

import abc
import contextlib
import os
import typing as t

import globus_sdk


class StorageAdapter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def store(self, token_response: globus_sdk.OAuthTokenResponse) -> None:
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

    def on_refresh(self, token_response: globus_sdk.OAuthTokenResponse) -> None:
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

    @staticmethod
    def _owner_only_opener(path: str, flags: int) -> int:
        """
        An ``opener`` for the builtin ``open()``.

        A new file will be created with the mode ``0o600``.
        An existing file will keep its existing mode.
        """

        try:
            # Open the file with a 0o600 mode set. (See below for a corner case.)
            # The O_CREAT | O_EXCL flags will trigger `FileExistsError`
            # if the file already exists.
            fd = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            # The file already exists. Open and return the descriptor immediately
            # to avoid falling through to the code below that changes the file mode.
            # Note: a dangling symlink will reach this line and raise an exception.
            return os.open(path, flags & ~os.O_CREAT)

        # Corner case: the 0o600 mode, set above, may be further restricted
        # by the process-level umask. Therefore, set the permissions exactly.
        try:
            os.fchmod(fd, 0o600)
        except (AttributeError, OSError):
            # `os.fchmod` doesn't exist on all platforms.
            # In addition, some filesystems do not support changing modes.
            pass

        return fd

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

        .. warning::

            This method is deprecated and will be removed in version 5.

            The umask of the entire Python process is changed, so it is not safe
            to use this method while other threads create files or use this method.
        """

        # In a context manager, the frames above this one are contextlib's
        # ``__enter__`` and then the caller's ``with`` statement.
        globus_sdk.exc.warn_deprecated(
            "'user_only_umask' is deprecated and will be removed in version 5. "
            "It changes the umask of the whole process, "
            "which is not safe when other threads are running.",
            stacklevel=4,
        )
        old_umask = os.umask(0o177)
        try:
            yield
        finally:
            os.umask(old_umask)
