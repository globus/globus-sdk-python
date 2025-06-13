import json
import urllib.parse

import pytest

from globus_sdk import MISSING
from globus_sdk._testing import RegisteredResponse, get_last_request, load_response


@pytest.fixture(autouse=True)
def setup_mock_responses():
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar",
            json={"foo": "bar"},
        )
    )
    load_response(
        RegisteredResponse(
            path="https://foo.api.globus.org/bar",
            method="POST",
            json={"foo": "bar"},
        )
    )


def test_query_params_can_filter_missing(client):
    res = client.get("/bar", query_params={"foo": "bar", "baz": MISSING})
    assert res.http_status == 200
    req = get_last_request()
    assert req.params == {"foo": "bar"}


def test_headers_can_filter_missing(client):
    res = client.get("/bar", headers={"foo": "bar", "baz": MISSING})
    assert res.http_status == 200
    req = get_last_request()
    assert req.headers["foo"] == "bar"
    assert "baz" not in req.headers


def test_json_body_can_filter_missing(client):
    res = client.post("/bar", data={"foo": "bar", "baz": MISSING})
    assert res.http_status == 200
    req = get_last_request()
    sent = json.loads(req.body)
    assert sent == {"foo": "bar"}


def test_form_body_can_filter_missing(client):
    res = client.post("/bar", data={"foo": "bar", "baz": MISSING}, encoding="form")
    assert res.http_status == 200
    req = get_last_request()
    sent = urllib.parse.parse_qs(req.body)
    assert sent == {"foo": ["bar"]}
