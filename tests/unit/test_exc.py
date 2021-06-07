import json
from collections import namedtuple

import pytest
import requests

from globus_sdk import AuthAPIError, TransferAPIError, exc

_TestResponse = namedtuple("_TestResponse", ("data", "r"))


def _mk_response(data, status, headers=None, data_transform=None):
    resp = requests.Response()

    if data_transform:
        resp._content = data_transform(data).encode("utf-8")
    else:
        resp._content = data.encode("utf-8")

    if headers:
        resp.headers.update(headers)

    resp.status_code = str(status)
    return _TestResponse(data, resp)


def _mk_json_response(data, status):
    return _mk_response(
        data,
        status,
        data_transform=json.dumps,
        headers={"Content-Type": "application/json"},
    )


@pytest.fixture
def json_response():
    json_data = {"errors": [{"message": "json error message", "code": "Json Error"}]}
    return _mk_json_response(json_data, 400)


@pytest.fixture
def text_response():
    text_data = "error message"
    return _mk_response(text_data, 401)


@pytest.fixture
def malformed_response():
    return _mk_response("{", 403)


@pytest.fixture
def transfer_response():
    transfer_data = {
        "message": "transfer error message",
        "code": "Transfer Error",
        "request_id": 123,
    }
    return _mk_json_response(transfer_data, 404)


@pytest.fixture
def simple_auth_response():
    auth_data = {"error": "simple auth error message"}
    return _mk_json_response(auth_data, 404)


@pytest.fixture
def nested_auth_response():
    auth_data = {
        "errors": [{"detail": "nested auth error message", "code": "Auth Error"}]
    }
    return _mk_json_response(auth_data, 404)


def test_raw_json_works(json_response):
    err = exc.GlobusAPIError(json_response.r)
    assert err.raw_json == json_response.data


def test_raw_json_fail(text_response, malformed_response):
    err = exc.GlobusAPIError(text_response.r)
    assert err.raw_json is None

    err = exc.GlobusAPIError(malformed_response.r)
    assert err.raw_json is None


def test_raw_text_works(json_response, text_response):
    err = exc.GlobusAPIError(json_response.r)
    assert err.raw_text == json.dumps(json_response.data)
    err = exc.GlobusAPIError(text_response.r)
    assert err.raw_text == text_response.data


def test_get_args(json_response, text_response, malformed_response):
    err = exc.GlobusAPIError(json_response.r)
    assert err._get_args() == ("400", "Json Error", "json error message")
    err = exc.GlobusAPIError(text_response.r)
    assert err._get_args() == ("401", "Error", "error message")
    err = exc.GlobusAPIError(malformed_response.r)
    assert err._get_args() == ("403", "Error", "{")


def test_get_args_transfer(
    json_response, text_response, malformed_response, transfer_response
):
    err = TransferAPIError(transfer_response.r)
    assert err._get_args() == ("404", "Transfer Error", "transfer error message", 123)

    # wrong format
    err = TransferAPIError(json_response.r)
    assert err._get_args() == ("400", "Error", json.dumps(json_response.data), None)
    # defaults for non-json
    err = TransferAPIError(text_response.r)
    assert err._get_args() == ("401", "Error", "error message", None)
    err = TransferAPIError(malformed_response.r)
    assert err._get_args() == ("403", "Error", "{", None)


def test_get_args_auth(
    json_response,
    text_response,
    malformed_response,
    simple_auth_response,
    nested_auth_response,
):
    err = AuthAPIError(simple_auth_response.r)
    assert err._get_args() == ("404", "Error", "simple auth error message")
    err = AuthAPIError(nested_auth_response.r)
    assert err._get_args() == ("404", "Auth Error", "nested auth error message")

    # wrong format, but similar/close
    err = AuthAPIError(json_response.r)
    assert err._get_args() == ("400", "Json Error", "json error message")

    # non-json
    err = AuthAPIError(text_response.r)
    assert err._get_args() == ("401", "Error", "error message")
    err = AuthAPIError(malformed_response.r)
    assert err._get_args() == ("403", "Error", "{")


@pytest.mark.parametrize(
    "orig, wrap_class",
    [
        (requests.RequestException("exc_message"), exc.NetworkError),
        (requests.Timeout("timeout_message"), exc.GlobusTimeoutError),
        (requests.ConnectionError("connection_message"), exc.GlobusConnectionError),
    ],
)
def test_requests_err_wrappers(orig, wrap_class):
    msg = "dummy message"
    err = wrap_class(msg, orig)
    assert err.underlying_exception == orig
    assert str(err) == msg


@pytest.mark.parametrize(
    "orig, conv_class",
    [
        (requests.RequestException("exc_message"), exc.NetworkError),
        (requests.Timeout("timeout_message"), exc.GlobusTimeoutError),
        (requests.ConnectionError("connection_message"), exc.GlobusConnectionError),
    ],
)
def test_convert_requests_exception(orig, conv_class):
    conv = exc.convert_request_exception(orig)
    assert conv.underlying_exception == orig
    assert isinstance(conv, conv_class)
