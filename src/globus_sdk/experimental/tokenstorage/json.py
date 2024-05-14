from __future__ import annotations

import json
import pathlib
import typing as t

from globus_sdk.experimental.tokenstorage.base import FileTokenStorage
from globus_sdk.version import __version__

from .token_data import TokenData


class JSONTokenStorage(FileTokenStorage):
    """
    A storage adapter for storing token data in JSON files.
    """

    # the version for the current data format used by the file adapter.
    # 1.0 was used by ``SimpleJSONFileAdapter``. If ``JSONFileAdapter`` is
    # pointed at storage used by a ``SimpleJSONFileAdapter` it will be converted to 2.0
    # and no longer usable by ``SimpleJSONFileAdapter``.
    format_version = "2.0"

    # the supported versions (data not in these versions causes an error)
    supported_versions = ("1.0", "2.0")

    def __init__(self, filename: pathlib.Path | str, *, namespace: str = "DEFAULT"):
        """
        :param filename: the name of the file to write to and read from
        :param namespace: A user-supplied namespace for partitioning token data
        """
        self.filename = str(filename)
        super().__init__(namespace=namespace)

    def _raw_load(self) -> dict[str, t.Any]:
        """
        Load the file contents as JSON and return the resulting dict
        object. If a dict is not found, raises an error.
        """
        with open(self.filename, encoding="utf-8") as f:
            val = json.load(f)
        if not isinstance(val, dict):
            raise ValueError("reading from json file got non-dict data")
        return val

    def _handle_formats(self, read_data: dict[str, t.Any]) -> dict[str, t.Any]:
        """Handle older data formats supported by this class

        if the data is not in a known/recognized format, this will error
        otherwise, reshape the data to the current supported format and return it
        """
        format_version = read_data.get("format_version")
        if format_version not in self.supported_versions:
            raise ValueError(
                f"cannot store data using SimpleJSONFileAdapter({self.filename} "
                "existing data file is in an unknown format "
                f"(format_version={format_version})"
            )

        # 1.0 data was stored under a "by_rs" key without namespaces, to upgrade we
        # move everything under the "DEFAULT" key and remove the "by_rs" key.
        if format_version == "1.0":
            read_data = {
                "data": {
                    "DEFAULT": read_data["by_rs"],
                },
                "format_version": self.format_version,
                "globus-sdk.version": __version__,
            }

        return read_data

    def _load(self) -> dict[str, t.Any]:
        """
        Load data from the file and ensure that the data is in a modern format which can
        be handled by the rest of the adapter.

        If the file is missing, this will return a "skeleton" for new data.
        """
        try:
            data = self._raw_load()
        except FileNotFoundError:
            return {
                "data": {},
                "format_version": self.format_version,
                "globus-sdk.version": __version__,
            }
        return self._handle_formats(data)

    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: dict[str, TokenData]
    ) -> None:
        """
        Store token data as JSON data in ``self.filename`` under the current namespace

        Additionally will write the version of ``globus_sdk``which was in use.

        Under the assumption that this may be running on a system with multiple
        local users, this sets the umask such that only the owner of the
        resulting file can read or write it.

        :param token_data_by_resource_server: a ``dict`` of ``TokenData`` objects
            indexed by their ``resource_server``.
        """
        to_write = self._load()

        # create the namespace if it does not exist
        if self.namespace not in to_write["data"]:
            to_write["data"][self.namespace] = {}

        # add token data by resource server to namespaced data
        for resource_server, token_data in token_data_by_resource_server.items():
            to_write["data"][self.namespace][resource_server] = token_data.to_dict()

        # update globus-sdk version
        to_write["globus-sdk.version"] = __version__

        # write the file, denying rwx to Group and World, exec to User
        with self.user_only_umask():
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(to_write, f)

    def get_token_data_by_resource_server(self) -> dict[str, TokenData]:
        """
        Lookup all token data under the current namespace from the JSON file.

        Returns a dict of ``TokenData`` objects indexed by their resource server.
        """
        # TODO: when the Globus SDK drops support for py3.6 and py3.7, we can update
        # `_load` to return a TypedDict which guarantees the response is a dict
        # see: https://www.python.org/dev/peps/pep-0589/
        ret = {}
        dicts_by_resource_server = t.cast(
            t.Dict[str, t.Any], self._load()["data"].get(self.namespace, {})
        )
        for resource_server, token_data_dict in dicts_by_resource_server.items():
            ret[resource_server] = TokenData.from_dict(token_data_dict)
        return ret

    def remove_token_data(self, resource_server: str) -> bool:
        """
        Remove all tokens for a resource server from the JSON data, then overwrite
        ``self.filename``.

        Returns True if token data was removed, False if none was found to remove.

        :param resource_server: The resource server string to remove tokens for
        """
        to_write = self._load()

        # pop the token data out if it exists
        popped = to_write["data"].get(self.namespace, {}).pop(resource_server, None)

        # overwrite the file, denying rwx to Group and World, exec to User
        with self.user_only_umask():
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(to_write, f)

        return popped is not None
