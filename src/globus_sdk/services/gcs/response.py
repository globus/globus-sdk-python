from __future__ import annotations

import re
import typing as t

from globus_sdk.response import GlobusHTTPResponse, IterableResponse


class IterableGCSResponse(IterableResponse):
    """
    Response class for non-paged list oriented resources. Allows top level
    fields to be accessed normally via standard item access, and also
    provides a convenient way to iterate over the sub-item list in the
    ``data`` key:

    >>> print("Path:", r["path"])
    >>> # Equivalent to: for item in r["data"]
    >>> for item in r:
    >>>     print(item["name"], item["type"])
    """

    default_iter_key = "data"


class UnpackingGCSResponse(GlobusHTTPResponse):
    """
    An "unpacking" response looks for a "data" array in the response data, which is
    expected to have dict elements. The "data" is traversed until the first matching
    object is found, and this is presented as the ``data`` property of the response.

    The full response data is available as ``full_data``.

    If the expected datatype is not found in the array, or the array is missing, the
    ``data`` will be the full response data (identical to ``full_data``).

    :param match: Either a string containing a DATA_TYPE prefix, or an arbitrary
        callable which does the matching
    :type match: str or callable
    """

    def _default_unpacking_match(
        self, spec: str
    ) -> t.Callable[[dict[str, t.Any]], bool]:
        if not re.fullmatch(r"\w+", spec):
            raise ValueError("Invalid UnpackingGCSResponse specification.")

        def match_func(data: dict[str, t.Any]) -> bool:
            if not ("DATA_TYPE" in data and isinstance(data["DATA_TYPE"], str)):
                return False
            if "#" not in data["DATA_TYPE"]:
                return False
            name, _version = data["DATA_TYPE"].split("#", 1)
            return name == spec

        return match_func

    def __init__(
        self,
        response: GlobusHTTPResponse,
        match: str | t.Callable[[dict[str, t.Any]], bool],
    ):
        super().__init__(response)

        if callable(match):
            self._match_func = match
        else:
            self._match_func = self._default_unpacking_match(match)

        self._unpacked_data: dict[str, t.Any] | None = None
        self._did_unpack = False

    @property
    def full_data(self) -> t.Any:
        """
        The full, parsed JSON response data.
        ``None`` if the data cannot be parsed as JSON.
        """
        return self._parsed_json

    def _unpack(self) -> dict[str, t.Any] | None:
        """
        Unpack the response from the `"data"` array, returning the first match found.
        If no matches are founds, or the data is the wrong shape, return None.
        """
        if isinstance(self._parsed_json, dict) and isinstance(
            self._parsed_json.get("data"), list
        ):
            for item in self._parsed_json["data"]:
                if isinstance(item, dict) and self._match_func(item):
                    return item
        return None

    @property
    def data(self) -> t.Any:
        # only do the unpacking operation once, as it may be expensive on large payloads
        if not self._did_unpack:
            self._unpacked_data = self._unpack()
            self._did_unpack = True

        if self._unpacked_data is not None:
            return self._unpacked_data
        return self._parsed_json
