from __future__ import annotations

import typing as t

from globus_sdk._internal import orjson_compat

if t.TYPE_CHECKING:
    import requests


class ResponseDecoder:
    """
    A response decoder takes a requests.Response object and decodes different parts of
    it as necessary.

    The base decoder defines common behaviors, but subclasses may override.
    """

    def get_body_json(self, response: requests.Response) -> t.Any:
        return response.json()


class OrjsonResponseDecoder(ResponseDecoder):
    def __init__(self) -> None:
        # eagerly error if one of these is ever constructed and 'orjson' is not
        # installed
        orjson_compat.require()

    def get_body_json(self, response: requests.Response) -> t.Any:
        return orjson_compat.loads(response.content)
