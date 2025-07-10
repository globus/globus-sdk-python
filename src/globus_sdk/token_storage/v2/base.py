from __future__ import annotations

import abc
import contextlib
import os
import pathlib
import re
import sys
import typing as t

import globus_sdk
from globus_sdk._types import UUIDLike

from .token_data import TokenStorageData

if t.TYPE_CHECKING:
    from globus_sdk.globus_app import GlobusAppConfig


class TokenStorage(metaclass=abc.ABCMeta):
    """
    The interface for interacting with a store of :class:`TokenStorageData` objects.

    Implementations must partition their token data objects by ``namespace``.
    Within a namespace, token data must be indexed by ``resource_server``.

    :param namespace: A unique string for partitioning token data (Default: "DEFAULT").

    :ivar globus_sdk.IDTokenDecoder | None id_token_decoder: A decoder to use
        when decoding ``id_token`` JWTs from Globus Auth. By default, a new decoder
        is used each time decoding is performed.
    """

    def __init__(self, namespace: str = "DEFAULT") -> None:
        self.namespace = namespace
        self.id_token_decoder: globus_sdk.IDTokenDecoder | None = None

    @abc.abstractmethod
    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: t.Mapping[str, TokenStorageData]
    ) -> None:
        """
        Store token data for one or more resource server in the current namespace.

        :param token_data_by_resource_server: mapping of resource server to token data.
        """

    @abc.abstractmethod
    def get_token_data_by_resource_server(self) -> dict[str, TokenStorageData]:
        """
        Retrieve all token data stored in the current namespace.

        :returns: a dict of ``TokenStorageData`` objects indexed by their
            resource server.
        """

    def get_token_data(self, resource_server: str) -> TokenStorageData | None:
        """
        Retrieve token data for a particular resource server in the current namespace.

        :param resource_server: The resource_server string to get token data for.
        :returns: token data if found or else None.
        """
        return self.get_token_data_by_resource_server().get(resource_server)

    @abc.abstractmethod
    def remove_token_data(self, resource_server: str) -> bool:
        """
        Remove token data for a resource server in the current namespace.

        :param resource_server: The resource server string to remove token data for.
        :returns: True if token data was deleted, False if none was found to delete.
        """

    def store_token_response(
        self, token_response: globus_sdk.OAuthTokenResponse
    ) -> None:
        """
        Store token data from an :class:`OAuthTokenResponse` in the current namespace.

        :param token_response: A token response object from an authentication flow.
        """
        token_data_by_resource_server = {}

        identity_id = self._extract_identity_id(token_response)

        for resource_server, token_dict in token_response.by_resource_server.items():
            token_data_by_resource_server[resource_server] = TokenStorageData(
                resource_server=token_dict["resource_server"],
                identity_id=identity_id,
                scope=token_dict["scope"],
                access_token=token_dict["access_token"],
                refresh_token=token_dict.get("refresh_token"),
                expires_at_seconds=token_dict["expires_at_seconds"],
                token_type=token_dict.get("token_type"),
            )
        self.store_token_data_by_resource_server(token_data_by_resource_server)

    def _extract_identity_id(
        self, token_response: globus_sdk.OAuthTokenResponse
    ) -> str | None:
        """
        Get identity_id from id_token if available.

        .. note::

            This method is private, but is used in ValidatingTokenStorage to
            override the extraction of ``identity_id`` information.

        Generalizing customization of ``identity_id`` extraction will require
        implementation of a user-facing mechanism for controlling calls to
        ``decode_id_token()``.
        """
        # dependent token responses cannot contain an `id_token` field, as the
        # top-level data is an array
        if isinstance(token_response, globus_sdk.OAuthDependentTokenResponse):
            return None

        if id_token := token_response.get("id_token"):
            if self.id_token_decoder:
                decoded_id_token = self.id_token_decoder.decode(id_token)
            else:
                decoded_id_token = token_response.decode_id_token()
            return decoded_id_token["sub"]  # type: ignore[no-any-return]
        else:
            return None


class FileTokenStorage(TokenStorage, metaclass=abc.ABCMeta):
    """
    A base class for token storages which store tokens in a local file.

    Common functionality for file-based token storages like file creation and class
    instantiation for a GlobusApp is defined here.

    :cvar file_format: The file format suffix associated with files of this type. This
        is used when constructing the file path for a GlobusApp.

    :param filepath: The path to a file where token data should be stored.
    :param namespace: A unique string for partitioning token data (Default: "DEFAULT").
    """

    # File suffix associated with files of this type (e.g., "csv")
    file_format: str = "_UNSET_"  # must be overridden by subclasses

    def __init__(
        self, filepath: pathlib.Path | str, *, namespace: str = "DEFAULT"
    ) -> None:
        """
        :param filepath: the name of the file to write to and read from
        :param namespace: A user-supplied namespace for partitioning token data
        """
        self.filepath = str(filepath)
        try:
            self._ensure_containing_dir_exists()
        except OSError as e:
            msg = (
                "Encountered an error while initializing the token storage file "
                f"'{self.filepath}'"
            )
            raise ValueError(msg) from e
        super().__init__(namespace=namespace)

    def __init_subclass__(cls, **kwargs: t.Any):
        if cls.file_format == "_UNSET_":
            raise TypeError(f"{cls.__name__} must set a 'file_format' class attribute")

    @classmethod
    def for_globus_app(
        cls,
        client_id: UUIDLike,
        app_name: str,
        config: GlobusAppConfig,
        namespace: str,
    ) -> TokenStorage:
        """
        Initialize a TokenStorage instance for a GlobusApp, using the supplied
        info to determine the file location.

        :param client_id: The client ID of the Globus App.
        :param app_name: The name of the Globus App.
        :param config: The GlobusAppConfig object for the Globus App.
        :param namespace: A user-supplied namespace for partitioning token data.
        """
        filepath = _default_globus_app_filepath(client_id, app_name, config.environment)
        return cls(filepath=f"{filepath}.{cls.file_format}", namespace=namespace)

    def _ensure_containing_dir_exists(self) -> None:
        """
        Ensure that the directory containing the given filepath exists.
        """
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def file_exists(self) -> bool:
        """
        Check if the file used by this file storage adapter exists.
        """
        return os.path.exists(self.filepath)

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


def _default_globus_app_filepath(
    client_id: UUIDLike, app_name: str, environment: str
) -> str:
    r"""
    Construct a default TokenStorage filepath for a GlobusApp.
    For flexibility, the filepath will omit the file format suffix.

    On Windows, this will be:
        ``~\AppData\Local\globus\app\{client_id}\{app_name}\tokens``

    On Linux and macOS, we use:
        ``~/.globus/app/{client_id}/{app_name}/tokens``
    """
    environment_prefix = f"{environment}-"
    if environment == "production":
        environment_prefix = ""
    filename = f"{environment_prefix}tokens"
    app_name = _slugify_app_name(app_name)

    if sys.platform == "win32":
        # try to get the app data dir, preferring the local appdata
        datadir = os.getenv("LOCALAPPDATA", os.getenv("APPDATA"))
        if not datadir:
            home = os.path.expanduser("~")
            datadir = os.path.join(home, "AppData", "Local")
        return os.path.join(
            datadir, "globus", "app", str(client_id), app_name, filename
        )
    else:
        return os.path.expanduser(
            f"~/.globus/app/{str(client_id)}/{app_name}/{filename}"
        )


# https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions
_RESERVED_FS_CHARS = re.compile(r'[<>:"/\\|?*]')
# https://stackoverflow.com/a/31976060
_RESERVED_FS_NAMES = re.compile(r"con|prn|aux|nul|com\d|lpt\d")


def _slugify_app_name(app_name: str) -> str:
    """
    Slugify a globus app name for use in a file path.

    * Reserved filesystem characters are replaced with a '+'. ('a?' -> 'a+')
    * Periods and Spaces are replaced with a '-'. ('a. b' -> 'a--b')
    * Control characters are removed. ('a\0b' -> 'ab')
    * The string is lowercased. ('AB' -> 'ab')

    :raises: GlobusSDKUsageError if the app name is empty after slugification.
    :raises: GlobusSDKUsageError if the app name is a reserved filesystem name (after
        slugification).
    """
    app_name = _RESERVED_FS_CHARS.sub("+", app_name)
    app_name = app_name.replace(".", "-").replace(" ", "-")
    app_name = "".join(c for c in app_name if c.isprintable())
    app_name = app_name.lower()

    if _RESERVED_FS_NAMES.fullmatch(app_name):
        msg = (
            f'App name results in a reserved filename ("{app_name}"). '
            "Please choose a different name."
        )
        raise globus_sdk.GlobusSDKUsageError(msg)

    if not app_name:
        msg = "App name results in the empty string. Please choose a different name."
        raise globus_sdk.GlobusSDKUsageError(msg)

    return app_name
