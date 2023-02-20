import http.client
import json
from collections import namedtuple

import pytest
import requests

_TestResponse = namedtuple("_TestResponse", ("data", "r", "method", "url"))


def _mk_response(
    data,
    status,
    method=None,
    url=None,
    headers=None,
    request_headers=None,
    data_transform=None,
):
    resp = requests.Response()

    if data_transform:
        resp._content = data_transform(data).encode("utf-8")
    else:
        resp._content = data.encode("utf-8")
    resp.encoding = "utf-8"

    if headers:
        resp.headers.update(headers)

    resp.status_code = str(status)
    resp.reason = http.client.responses.get(status, "Unknown")
    method = method or "GET"
    url = url or "default-example-url.bogus"
    resp.url = url
    resp.request = requests.Request(method=method, url=url, headers=request_headers)
    return _TestResponse(data, resp, method, url)


@pytest.fixture
def make_response():
    return _mk_response


@pytest.fixture
def make_json_response():
    def func(data, status):
        return _mk_response(
            data,
            status,
            data_transform=json.dumps,
            headers={"Content-Type": "application/json"},
        )

    return func


@pytest.fixture
def success_response():
    return _mk_response("{}", 200)


@pytest.fixture
def default_json_response(make_json_response):
    json_data = {
        "errors": [
            {
                "message": "json error message",
                "title": "json error message",
                "code": "Json Error",
            }
        ]
    }
    return make_json_response(json_data, 400)


@pytest.fixture
def default_text_response():
    return _mk_response("error message", 401)


@pytest.fixture
def malformed_response():
    return _mk_response("{", 403, headers={"Content-Type": "application/json"})
