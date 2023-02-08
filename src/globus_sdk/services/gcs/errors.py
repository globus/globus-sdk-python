from __future__ import annotations

import typing as t

import requests

from globus_sdk import exc


class GCSAPIError(exc.GlobusAPIError):
    """
    Error class for the GCS Manager API client
    """

    def __init__(self, r: requests.Response) -> None:
        self.detail_data_type: str | None = None
        self.detail: None | str | dict[str, t.Any] = None
        super().__init__(r)

    def _get_args(self) -> list[t.Any]:
        args = super()._get_args()
        args.append(self.detail_data_type)
        # only add detail if it's a string (don't want to put a large object into
        # stacktraces)
        if isinstance(self.detail, str):
            args.append(self.detail)
        return args

    def _load_from_json(self, data: dict[str, t.Any]) -> None:
        super()._load_from_json(data)
        # detail can be a full document, so fetch, then look for a DATA_TYPE
        # and expose it as a top-level attribute for easy access
        self.detail = data.get("detail")
        if isinstance(self.detail, dict) and "DATA_TYPE" in self.detail:
            self.detail_data_type = self.detail["DATA_TYPE"]
