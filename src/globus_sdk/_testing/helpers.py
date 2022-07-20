from typing import Optional, cast

import requests
import responses


def get_last_request(
    *, requests_mock: Optional[responses.RequestsMock] = None
) -> Optional[requests.PreparedRequest]:
    calls = requests_mock.calls if requests_mock is not None else responses.calls
    try:
        return cast(requests.PreparedRequest, calls[-1].request)
    except IndexError:
        return None
