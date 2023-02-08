from __future__ import annotations

import typing as t

import requests

from globus_sdk import exc


class SearchAPIError(exc.GlobusAPIError):
    """
    Error class for the Search API client. In addition to the
    inherited ``code`` and ``message`` instance variables, provides ``error_data``.

    :ivar error_data: Additional object returned in the error response. May be
                      a dict, list, or None.
    """

    # the Search API always and only returns 'message' for string messages
    MESSAGE_FIELDS = ["message"]

    def __init__(self, r: requests.Response) -> None:
        self.error_data = None
        super().__init__(r)

    def _load_from_json(self, data: dict[str, t.Any]) -> None:
        super()._load_from_json(data)
        self.error_data = data.get("error_data")
