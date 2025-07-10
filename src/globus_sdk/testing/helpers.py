from __future__ import annotations

import http.client
import json
import typing as t

import requests
import responses

from globus_sdk.exc import GlobusAPIError

E = t.TypeVar("E", bound=GlobusAPIError)


def get_last_request(
    *, requests_mock: responses.RequestsMock | None = None
) -> requests.PreparedRequest | None:
    """
    Get the last request which was received, or None if there were no requests.

    :param requests_mock: A non-default ``RequestsMock`` object to use.
    """
    calls = requests_mock.calls if requests_mock is not None else responses.calls
    try:
        last_call = calls[-1]
    except IndexError:
        return None
    return last_call.request


@t.overload
def construct_error(
    *,
    http_status: int,
    body: bytes | str | t.Dict[str, t.Any],
    method: str = "GET",
    response_headers: t.Dict[str, str] | None = None,
    request_headers: t.Dict[str, str] | None = None,
    response_encoding: str = "utf-8",
    url: str = "https://bogus-url/",
) -> GlobusAPIError: ...


@t.overload
def construct_error(
    *,
    http_status: int,
    error_class: type[E],
    body: bytes | str | t.Dict[str, t.Any],
    method: str = "GET",
    response_headers: t.Dict[str, str] | None = None,
    request_headers: t.Dict[str, str] | None = None,
    response_encoding: str = "utf-8",
    url: str = "https://bogus-url/",
) -> E: ...


def construct_error(
    *,
    http_status: int,
    body: bytes | str | t.Dict[str, t.Any],
    error_class: type[E] | type[GlobusAPIError] = GlobusAPIError,
    method: str = "GET",
    response_headers: t.Dict[str, str] | None = None,
    request_headers: t.Dict[str, str] | None = None,
    response_encoding: str = "utf-8",
    url: str = "https://bogus-url/",
) -> E | GlobusAPIError:
    """
    Given parameters for an HTTP response, construct a GlobusAPIError and return it.

    :param error_class: The class of the error to construct. Defaults to
        GlobusAPIError.
    :param http_status: The HTTP status code to use in the response.
    :param body: The body of the response. If a dict, will be JSON-encoded.
    :param method: The HTTP method to set on the underlying request.
    :param response_headers: The headers of the response.
    :param request_headers: The headers of the request.
    :param response_encoding: The encoding to use for the response body.
    :param url: The URL to set on the underlying request.
    """
    raw_response = requests.Response()
    raw_response.status_code = http_status
    raw_response.reason = http.client.responses.get(http_status, "Unknown")
    raw_response.url = url
    raw_response.encoding = response_encoding
    raw_response.request = requests.Request(
        method=method, url=url, headers=request_headers or {}
    ).prepare()
    raw_response.headers.update(response_headers or {})
    if isinstance(body, dict) and "Content-Type" not in raw_response.headers:
        raw_response.headers["Content-Type"] = "application/json"

    raw_response._content = _encode_body(body, response_encoding)

    return error_class(raw_response)


def _encode_body(body: bytes | str | t.Dict[str, t.Any], encoding: str) -> bytes:
    if isinstance(body, bytes):
        return body
    elif isinstance(body, str):
        return body.encode(encoding)
    else:
        return json.dumps(body).encode(encoding)
