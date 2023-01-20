import typing as t

import requests
import responses


def get_last_request(
    *, requests_mock: t.Optional[responses.RequestsMock] = None
) -> t.Optional[requests.PreparedRequest]:
    calls = requests_mock.calls if requests_mock is not None else responses.calls
    try:
        last_call = t.cast(responses.Call, calls[-1])
    except IndexError:
        return None
    return t.cast(requests.PreparedRequest, last_call.request)
