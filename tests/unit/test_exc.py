import itertools
import json
from collections import namedtuple

import pytest
import requests

from globus_sdk import AuthAPIError, TransferAPIError, exc

_TestResponse = namedtuple("_TestResponse", ("data", "r", "method", "url"))


def _strmatch_any_order(inputstr, prefix, midfixes, suffix, sep=", "):
    # test for string matching, but without insisting on ordering of middle segments
    assert inputstr in [
        prefix + sep.join(m) + suffix for m in itertools.permutations(midfixes)
    ]


def _mk_response(
    data, status, method=None, url=None, headers=None, data_transform=None
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
    method = method or "GET"
    url = url or "default-example-url.bogus"
    resp.url = url
    resp.request = requests.Request(method=method, url=url, headers=headers)
    return _TestResponse(data, resp, method, url)


_DEFAULT_RESPONSE = _mk_response("{}", 200)


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
    return _mk_response("{", 403, headers={"Content-Type": "application/json"})


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
        "errors": [
            {"detail": "nested auth error message", "code": "Auth Error"},
            {
                "message": "some other error which will not be seen",
                "code": "HiddenError",
            },
        ]
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
    assert err._get_args() == [
        json_response.method,
        json_response.url,
        None,
        "400",
        "Json Error",
        "json error message",
    ]
    err = exc.GlobusAPIError(text_response.r)
    assert err._get_args() == [
        text_response.method,
        text_response.url,
        None,
        "401",
        "Error",
        "error message",
    ]
    err = exc.GlobusAPIError(malformed_response.r)
    assert err._get_args() == [
        text_response.method,
        text_response.url,
        None,
        "403",
        "Error",
        "{",
    ]


def test_get_args_transfer(
    json_response, text_response, malformed_response, transfer_response
):
    err = TransferAPIError(transfer_response.r)
    assert err._get_args() == [
        _DEFAULT_RESPONSE.method,
        _DEFAULT_RESPONSE.url,
        None,
        "404",
        "Transfer Error",
        "transfer error message",
        123,
    ]

    # wrong format (but still parseable)
    err = TransferAPIError(json_response.r)
    assert err._get_args() == [
        _DEFAULT_RESPONSE.method,
        _DEFAULT_RESPONSE.url,
        None,
        "400",
        "Json Error",
        "json error message",
        None,
    ]
    # defaults for non-json
    err = TransferAPIError(text_response.r)
    assert err._get_args() == [
        _DEFAULT_RESPONSE.method,
        _DEFAULT_RESPONSE.url,
        None,
        "401",
        "Error",
        "error message",
        None,
    ]
    err = TransferAPIError(malformed_response.r)
    assert err._get_args() == [
        _DEFAULT_RESPONSE.method,
        _DEFAULT_RESPONSE.url,
        None,
        "403",
        "Error",
        "{",
        None,
    ]


def test_get_args_auth(
    json_response,
    text_response,
    malformed_response,
    simple_auth_response,
    nested_auth_response,
):
    err = AuthAPIError(simple_auth_response.r)
    assert err._get_args() == [
        _DEFAULT_RESPONSE.method,
        _DEFAULT_RESPONSE.url,
        None,
        "404",
        "Error",
        "simple auth error message",
    ]
    err = AuthAPIError(nested_auth_response.r)
    assert err._get_args() == [
        _DEFAULT_RESPONSE.method,
        _DEFAULT_RESPONSE.url,
        None,
        "404",
        "Auth Error",
        "nested auth error message",
    ]

    # wrong format, but similar/close
    err = AuthAPIError(json_response.r)
    assert err._get_args() == [
        _DEFAULT_RESPONSE.method,
        _DEFAULT_RESPONSE.url,
        None,
        "400",
        "Json Error",
        "json error message",
    ]

    # non-json
    err = AuthAPIError(text_response.r)
    assert err._get_args() == [
        _DEFAULT_RESPONSE.method,
        _DEFAULT_RESPONSE.url,
        None,
        "401",
        "Error",
        "error message",
    ]
    err = AuthAPIError(malformed_response.r)
    assert err._get_args() == [
        _DEFAULT_RESPONSE.method,
        _DEFAULT_RESPONSE.url,
        None,
        "403",
        "Error",
        "{",
    ]


def test_get_args_on_unknown_json():
    res = _mk_json_response({"foo": "bar"}, 400)
    err = exc.GlobusAPIError(res.r)
    assert err._get_args() == [
        res.method,
        res.url,
        None,
        "400",
        "Error",
        '{"foo": "bar"}',
    ]


def test_get_args_on_non_dict_json():
    res = _mk_json_response(["foo", "bar"], 400)
    err = exc.GlobusAPIError(res.r)
    assert err._get_args() == [
        res.method,
        res.url,
        None,
        "400",
        "Error",
        '["foo", "bar"]',
    ]


def test_info_is_falsey_on_non_dict_json():
    res = _mk_json_response(["foo", "bar"], 400)
    err = exc.GlobusAPIError(res.r)
    assert bool(err.info.consent_required) is False
    assert bool(err.info.authorization_parameters) is False
    assert str(err.info) == "AuthorizationParameterInfo(:)|ConsentRequiredInfo(:)"


def test_consent_required_info():
    res = _mk_json_response(
        {"code": "ConsentRequired", "required_scopes": ["foo", "bar"]}, 401
    )
    err = exc.GlobusAPIError(res.r)
    assert bool(err.info.consent_required) is True
    assert err.info.consent_required.required_scopes == ["foo", "bar"]
    assert str(err.info.consent_required) == (
        "ConsentRequiredInfo(required_scopes=['foo', 'bar'])"
    )

    # if the code is right but the scope list is missing, it should be falsey
    res = _mk_json_response({"code": "ConsentRequired"}, 401)
    err = exc.GlobusAPIError(res.r)
    assert bool(err.info.consent_required) is False
    assert err.info.consent_required.required_scopes is None
    assert str(err.info.consent_required) == "ConsentRequiredInfo(:)"


def test_authz_params_info():
    res = _mk_json_response(
        {"authorization_parameters": {"session_message": "foo"}}, 401
    )
    err = exc.GlobusAPIError(res.r)
    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_message == "foo"
    assert err.info.authorization_parameters.session_required_identities is None
    assert err.info.authorization_parameters.session_required_single_domain is None
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=foo",
            "session_required_identities=None",
            "session_required_single_domain=None",
        ],
        ")",
    )

    res = _mk_json_response(
        {"authorization_parameters": {"session_required_identities": ["foo", "bar"]}},
        401,
    )
    err = exc.GlobusAPIError(res.r)
    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_message is None
    assert err.info.authorization_parameters.session_required_identities == [
        "foo",
        "bar",
    ]
    assert err.info.authorization_parameters.session_required_single_domain is None
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=None",
            "session_required_identities=['foo', 'bar']",
            "session_required_single_domain=None",
        ],
        ")",
    )

    res = _mk_json_response(
        {
            "authorization_parameters": {
                "session_required_single_domain": ["foo", "bar"]
            }
        },
        401,
    )
    err = exc.GlobusAPIError(res.r)
    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_message is None
    assert err.info.authorization_parameters.session_required_identities is None
    assert err.info.authorization_parameters.session_required_single_domain == [
        "foo",
        "bar",
    ]
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=None",
            "session_required_identities=None",
            "session_required_single_domain=['foo', 'bar']",
        ],
        ")",
    )


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
