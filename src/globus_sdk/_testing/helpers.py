from __future__ import annotations

import typing as t

import requests
import responses


def get_last_request(
    *, requests_mock: responses.RequestsMock | None = None
) -> requests.PreparedRequest | None:
    """
    Get the last request which was received, or None if there were no requests.

    :param requests_mock: A non-default ``RequestsMock`` object to use.
    :type requests_mock: responses.RequestsMock
    """
    calls = requests_mock.calls if requests_mock is not None else responses.calls
    try:
        last_call = t.cast(responses.Call, calls[-1])
    except IndexError:
        return None
    return t.cast(requests.PreparedRequest, last_call.request)
