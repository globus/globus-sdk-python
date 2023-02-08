from __future__ import annotations

import os
import typing as t

from globus_sdk.exc import GlobusSDKUsageError

from .owner_info import GlobusConnectPersonalOwnerInfo

if t.TYPE_CHECKING:
    import globus_sdk


def _on_windows() -> bool:
    """
    Per python docs, this is a safe, reliable way of checking the platform.
    sys.platform offers more detail -- more than we want, in this case.
    """
    return os.name == "nt"


class LocalGlobusConnectPersonal:
    r"""
    A LocalGlobusConnectPersonal object represents the available SDK methods
    for inspecting and controlling a running Globus Connect Personal
    installation.

    These objects do *not* inherit from BaseClient and do not provide methods
    for interacting with any Globus Service APIs.

    :param config_dir: Path to a non-default configuration directory. On Linux, this is
        the same as the value passed to Globus Connect Personal's `-dir` flag
        (i.e. the default value is ``~/.globusonline``).
    :type config_dir: str, optional
    """

    def __init__(self, *, config_dir: str | None = None) -> None:
        self._config_dir = config_dir
        self._endpoint_id: str | None = None

    def _detect_config_dir(self) -> str:
        if _on_windows():
            appdata = os.getenv("LOCALAPPDATA")
            if appdata is None:
                raise GlobusSDKUsageError(
                    "LOCALAPPDATA not detected in Windows environment. "
                    "Either ensure this variable is set or pass an explicit "
                    "config_dir to LocalGlobusConnectPersonal"
                )
            return os.path.join(appdata, "Globus Connect")
        return os.path.expanduser("~/.globusonline")

    @property
    def config_dir(self) -> str:
        """
        The ``config_dir`` for this endpoint.

        If no directory was given during initialization, this will be computed
        based on the current platform and environment.
        """
        if not self._config_dir:
            self._config_dir = self._detect_config_dir()
        return self._config_dir

    @property
    def _local_data_dir(self) -> str:
        return (
            self.config_dir if _on_windows() else os.path.join(self.config_dir, "lta")
        )

    @t.overload
    def get_owner_info(
        self,
    ) -> globus_sdk.GlobusConnectPersonalOwnerInfo | None:
        ...

    @t.overload
    def get_owner_info(
        self, auth_client: None
    ) -> globus_sdk.GlobusConnectPersonalOwnerInfo | None:
        ...

    @t.overload
    def get_owner_info(
        self, auth_client: globus_sdk.AuthClient
    ) -> dict[str, t.Any] | None:
        ...

    def get_owner_info(
        self, auth_client: globus_sdk.AuthClient | None = None
    ) -> None | globus_sdk.GlobusConnectPersonalOwnerInfo | dict[str, t.Any]:
        """
        Look up the local GCP information, returning a
        :class:`GlobusConnectPersonalOwnerInfo` object. The result may have an ``id`` or
        ``username`` set (depending on the underlying data).

        If you pass an AuthClient, this method will return a dict from the Get
        Identities API instead of the info object. This can fail (e.g. with network
        errors if there is no connectivity), so passing this value should be coupled
        with additional error handling.

        In either case, the result may be ``None`` if the data is missing or cannot be
        parsed.

        .. note::

            The data returned by this method is not checked for accuracy. It is
            possible for a user to modify the files used by GCP to list a different
            user.

        :param auth_client: An AuthClient to use to lookup the full identity information
            for the GCP owner
        :type auth_client: globus_sdk.AuthClient

        **Examples**

        Getting a username:

        >>> from globus_sdk import LocalGlobusConnectPersonal
        >>> local_gcp = LocalGlobusConnectPersonal()
        >>> local_gcp.get_owner_info()
        GlobusConnectPersonalOwnerInfo(username='foo@globusid.org')

        or you may get back an ID:

        >>> local_gcp = LocalGlobusConnectPersonal()
        >>> local_gcp.get_owner_info()
        GlobusConnectPersonalOwnerInfo(id='7deda7cc-077b-11ec-a137-67523ecffd4b')

        Check the result easily by looking to see if these values are ``None``:

        >>> local_gcp = LocalGlobusConnectPersonal()
        >>> info = local_gcp.get_owner_info()
        >>> has_username = info.username is not None
        """
        fname = os.path.join(self._local_data_dir, "gridmap")
        try:
            # read file data into an owner info object
            try:
                owner_info = GlobusConnectPersonalOwnerInfo._from_file(fname)
            except ValueError:  # may ValueError on invalid DN data
                return None
        except OSError as e:
            # no such file or directory
            if e.errno == 2:
                return None
            raise

        if auth_client is None:
            return owner_info

        if owner_info.id is not None:
            res = auth_client.get_identities(ids=owner_info.id)
        elif owner_info.username is not None:
            res = auth_client.get_identities(usernames=owner_info.username)
        else:  # pragma: no cover
            raise ValueError("Something went wrong. Could not parse owner info.")

        try:  # could get no data back in theory, if the identity isn't visible
            return t.cast(t.Dict[str, t.Any], res["identities"][0])
        except (KeyError, IndexError):
            return None

    @property
    def endpoint_id(self) -> str | None:
        """
        :type: str

        The endpoint ID of the local Globus Connect Personal endpoint
        installation.

        This value is loaded whenever it is first accessed, but saved after
        that.

        .. note::

            This attribute is not checked for accuracy. It is possible for a user to
            modify the files used by GCP to list a different ``endpoint_id``.

        Usage:

        >>> from globus_sdk import TransferClient, LocalGlobusConnectPersonal
        >>> local_ep = LocalGlobusConnectPersonal()
        >>> ep_id = local_ep.endpoint_id
        >>> tc = TransferClient(...)  # needs auth details
        >>> for f in tc.operation_ls(ep_id):
        >>>     print("Local file: ", f["name"])

        You can also reset the value, causing it to load again on next access,
        with ``del local_ep.endpoint_id``
        """
        if self._endpoint_id is None:
            fname = os.path.join(self._local_data_dir, "client-id.txt")
            try:
                with open(fname, encoding="utf-8") as fp:
                    self._endpoint_id = fp.read().strip()
            except OSError as e:
                # no such file or directory gets ignored, everything else reraise
                if e.errno != 2:
                    raise
        return self._endpoint_id

    @endpoint_id.deleter
    def endpoint_id(self) -> None:
        """
        Deleter for LocalGlobusConnectPersonal.endpoint_id
        """
        self._endpoint_id = None
