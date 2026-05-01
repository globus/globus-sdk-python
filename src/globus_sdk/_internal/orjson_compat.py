from __future__ import annotations

import json
import typing as t

from globus_sdk import config

if t.TYPE_CHECKING:
    import requests

dumps: t.Callable[[t.Any], bytes]
loads: t.Callable[[str | bytes], t.Any]
try:
    import orjson

    ORJSON_AVAILABLE: bool = True
except ImportError:
    ORJSON_AVAILABLE = False

    def dumps(obj: t.Any) -> bytes:
        return json.dumps(obj).encode()

    def loads(data: str | bytes) -> t.Any:
        return json.loads(data)

else:
    dumps = orjson.dumps
    loads = orjson.loads


def get_response_loader() -> t.Callable[[requests.Response], t.Any]:
    # IMPORTANT: getting the config setting can error, so this function
    # must be called outside of any error handling context for reading the response data
    # which would catch ValueErrors
    if ORJSON_AVAILABLE and config.get_prefer_orjson():

        def loader(r: requests.Response) -> t.Any:
            return loads(r.content)

    else:

        def loader(r: requests.Response) -> t.Any:
            return r.json()

    return loader
