from __future__ import annotations

import json
import pathlib
import typing as t


class LocalGlobusConnectServer:
    r"""
    A LocalGlobusConnectServer object represents the available SDK methods
    for inspecting and controlling a running Globus Connect Server
    installation.

    These objects do *not* inherit from BaseClient and do not provide methods
    for interacting with any Globus Service APIs.

    :param info_path: The path to the info file used to inspect the local system
    :type info_path: str, optional
    """

    def __init__(
        self,
        *,
        info_path: (str | pathlib.Path) = "/var/lib/globus-connect-server/info.json",
    ) -> None:
        self.info_path = pathlib.Path(info_path)
        self._loaded_info: dict[str, t.Any] | None = None

    @property
    def info_dict(self) -> dict[str, t.Any] | None:
        """
        The info.json data for the local Globus Connect Server, as a dict.

        If the info.json file is not present or cannot be parsed, the data is None.
        This indicates that there is no local Globus Connect Server node, or if there is
        one, it cannot be used or examined by the SDK. For example, containerized
        applications using the SDK may not be able to interact with Globus Connect
        Server on the container host.

        :type: dict or None
        """
        if self._loaded_info is None:
            if self.info_path.is_file():
                with open(self.info_path, encoding="utf-8") as fp:
                    try:
                        parsed_data = json.load(fp)
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        pass
                    else:
                        if isinstance(parsed_data, dict):
                            self._loaded_info = t.cast(t.Dict[str, t.Any], parsed_data)
        return self._loaded_info

    @info_dict.deleter
    def info_dict(self) -> None:
        self._loaded_info = None

    @property
    def endpoint_id(self) -> str | None:
        """
        The endpoint ID of the local Globus Connect Server endpoint.
        None if the data cannot be loaded or is malformed.

        :type: str or None
        """
        if self.info_dict is not None:
            epid = self.info_dict.get("endpoint_id")
            if isinstance(epid, str):
                return epid
        return None

    @property
    def domain_name(self) -> str | None:
        """
        The domain name of the local Globus Connect Server endpoint.
        None if the data cannot be loaded or is malformed.

        :type: str or None
        """
        if self.info_dict is not None:
            domain = self.info_dict.get("domain_name")
            if isinstance(domain, str):
                return domain
        return None
