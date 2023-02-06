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
    resp.reason = {
        200: "OK",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Server Error",
    }.get(status, "Unknown")
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
    json_data = {
        "errors": [
            {
                "message": "json error message",
                "title": "json error message",
                "code": "Json Error",
            }
        ]
    }
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
    auth_data = {"detail": "simple auth error message"}
    return _mk_json_response(auth_data, 404)


@pytest.fixture
def nested_auth_response():
    auth_data = {
        "errors": [
            {"detail": "nested auth error message", "code": "Auth Error"},
            {
                "title": "some other error which will not be seen",
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


def test_authz_params_info_containing_session_message():
    res = _mk_json_response(
        {"authorization_parameters": {"session_message": "foo"}}, 401
    )
    err = exc.GlobusAPIError(res.r)
    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_message == "foo"
    assert err.info.authorization_parameters.session_required_identities is None
    assert err.info.authorization_parameters.session_required_single_domain is None
    assert err.info.authorization_parameters.session_required_policies is None
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=foo",
            "session_required_identities=None",
            "session_required_single_domain=None",
            "session_required_policies=None",
        ],
        ")",
    )


def test_authz_params_info_containing_session_required_identities():
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
    assert err.info.authorization_parameters.session_required_policies is None
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=None",
            "session_required_identities=['foo', 'bar']",
            "session_required_single_domain=None",
            "session_required_policies=None",
        ],
        ")",
    )


def test_authz_params_info_containing_session_required_single_domain():
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
    assert err.info.authorization_parameters.session_required_policies is None
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=None",
            "session_required_identities=None",
            "session_required_single_domain=['foo', 'bar']",
            "session_required_policies=None",
        ],
        ")",
    )


def test_authz_params_info_containing_session_required_policies():
    res = _mk_json_response(
        {"authorization_parameters": {"session_required_policies": "foo,bar"}}, 401
    )
    err = exc.GlobusAPIError(res.r)
    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_message is None
    assert err.info.authorization_parameters.session_required_identities is None
    assert err.info.authorization_parameters.session_required_single_domain is None
    assert err.info.authorization_parameters.session_required_policies == ["foo", "bar"]
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=None",
            "session_required_identities=None",
            "session_required_single_domain=None",
            "session_required_policies=['foo', 'bar']",
        ],
        ")",
    )


def test_authz_params_info_containing_malformed_session_required_policies():
    # confirm that if `session_required_policies` is not a string,
    # it will parse as `None`
    res = _mk_json_response(
        {"authorization_parameters": {"session_required_policies": ["foo"]}}, 401
    )
    err = exc.GlobusAPIError(res.r)
    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_required_policies is None
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=None",
            "session_required_identities=None",
            "session_required_single_domain=None",
            "session_required_policies=None",
        ],
        ")",
    )


@pytest.mark.parametrize(
    "orig, wrap_class",
    [
        (requests.RequestException("exc_message"), exc.NetworkError),
        (requests.Timeout("timeout_message"), exc.GlobusTimeoutError),
        (
            requests.ConnectTimeout("connect_timeout_message"),
            exc.GlobusConnectionTimeoutError,
        ),
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
        (
            requests.ConnectTimeout("connect_timeout_message"),
            exc.GlobusConnectionTimeoutError,
        ),
        (requests.ConnectionError("connection_message"), exc.GlobusConnectionError),
    ],
)
def test_convert_requests_exception(orig, conv_class):
    conv = exc.convert_request_exception(orig)
    assert conv.underlying_exception == orig
    assert isinstance(conv, conv_class)


@pytest.mark.parametrize(
    "status, expect_reason",
    [
        (400, "Bad Request"),
        (500, "Server Error"),
    ],
)
def test_http_reason_exposure(status, expect_reason):
    res = _mk_response(
        {"errors": [{"message": "json error message", "code": "Json Error"}]},
        status,
        data_transform=json.dumps,
        headers={"Content-Type": "application/json"},
    )
    err = exc.GlobusAPIError(res.r)
    assert err.http_reason == expect_reason


def test_http_header_exposure():
    res = _mk_response(
        {"errors": [{"message": "json error message", "code": "Json Error"}]},
        400,
        data_transform=json.dumps,
        headers={"Content-Type": "application/json", "Spam": "Eggs"},
    )
    err = exc.GlobusAPIError(res.r)
    assert err.headers["spam"] == "Eggs"
    assert err.headers["Content-Type"] == "application/json"


# do not parametrize each of these independently: it would result in hundreds of tests
# which are not meaningfully non-overlapping in what they test
# instead, iterate through "full variations" to keep the suite faster
@pytest.mark.parametrize(
    "http_method, http_status, error_code, request_url, error_message, authz_scheme",
    [
        (
            "POST",
            404,
            "FooError",
            "https://bogus.example.com/foo",
            "got a foo error",
            "bearer",
        ),
        ("PATCH", 500, None, "https://bogus.example.org/bar", "", "unknown-token"),
        ("PUT", 501, None, "https://bogus.example.org/bar", None, None),
    ],
)
def test_error_repr_has_expected_info(
    http_method, http_status, authz_scheme, request_url, error_code, error_message
):
    http_reason = {404: "Not Found", 500: "Server Error", 501: "Not Implemented"}.get(
        http_status
    )

    body = {"otherfield": "otherdata"}
    if error_code is not None:
        body["code"] = error_code
    if error_message is not None:
        body["message"] = error_message

    headers = {"Content-Type": "application/json", "Spam": "Eggs"}
    if authz_scheme is not None:
        headers["Authorization"] = f"{authz_scheme} TOKENINFO"

    # build the response -> error -> error repr
    res = _mk_response(
        body,
        http_status,
        method=http_method,
        data_transform=json.dumps,
        url=request_url,
        headers=headers,
    )
    err = exc.GlobusAPIError(res.r)
    stringified = repr(err)

    # check using substring -- do not check exact format
    assert http_method in stringified
    assert request_url in stringified
    if authz_scheme in exc.GlobusAPIError.RECOGNIZED_AUTHZ_SCHEMES:
        assert authz_scheme in stringified
    # confirm that actual tokens don't get into the repr, regardless of authz scheme
    assert "TOKENINFO" not in stringified
    assert str(http_status) in stringified
    if error_code is not None:
        assert error_code in stringified
    else:
        assert "'Error'" in stringified
    if error_message is None:
        assert "otherdata" in stringified
    else:
        assert "otherdata" not in stringified
        if error_message:
            assert error_message in stringified
        else:
            assert http_reason in stringified
