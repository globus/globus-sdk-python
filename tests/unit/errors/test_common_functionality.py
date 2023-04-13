import itertools
import json

import pytest
import requests

from globus_sdk import GlobusAPIError, RemovedInV4Warning, exc


def _strmatch_any_order(inputstr, prefix, midfixes, suffix, sep=", "):
    # test for string matching, but without insisting on ordering of middle segments
    assert inputstr in [
        prefix + sep.join(m) + suffix for m in itertools.permutations(midfixes)
    ]


def test_raw_json_works(default_json_response):
    err = GlobusAPIError(default_json_response.r)
    assert err.raw_json == default_json_response.data


def test_raw_json_fail(default_text_response, malformed_response):
    err = GlobusAPIError(default_text_response.r)
    assert err.raw_json is None

    err = GlobusAPIError(malformed_response.r)
    assert err.raw_json is None


def test_text_property_works(default_json_response, default_text_response):
    err = GlobusAPIError(default_json_response.r)
    assert err.text == json.dumps(default_json_response.data)
    err = GlobusAPIError(default_text_response.r)
    assert err.text == default_text_response.data


def test_binary_content_property(default_text_response):
    err = GlobusAPIError(default_text_response.r)
    assert err.binary_content == default_text_response.data.encode("utf-8")


def test_raw_text_property_works_but_warns(
    default_json_response, default_text_response
):
    err = GlobusAPIError(default_json_response.r)
    with pytest.warns(
        RemovedInV4Warning,
        match=(
            r"The 'raw_text' property of GlobusAPIError objects is deprecated\. "
            r"Use the 'text' property instead\."
        ),
    ):
        assert err.raw_text == json.dumps(default_json_response.data)


def test_get_args(default_json_response, default_text_response, malformed_response):
    err = GlobusAPIError(default_json_response.r)
    assert err._get_args() == [
        default_json_response.method,
        default_json_response.url,
        None,
        "400",
        "Json Error",
        "json error message",
    ]
    err = GlobusAPIError(default_text_response.r)
    assert err._get_args() == [
        default_text_response.method,
        default_text_response.url,
        None,
        "401",
        "Error",
        "error message",
    ]
    err = GlobusAPIError(malformed_response.r)
    assert err._get_args() == [
        default_text_response.method,
        default_text_response.url,
        None,
        "403",
        "Error",
        "{",
    ]


def test_get_args_on_unknown_json(make_json_response):
    res = make_json_response({"foo": "bar"}, 400)
    err = GlobusAPIError(res.r)
    assert err._get_args() == [
        res.method,
        res.url,
        None,
        "400",
        "Error",
        '{"foo": "bar"}',
    ]


def test_get_args_on_non_dict_json(make_json_response):
    res = make_json_response(["foo", "bar"], 400)
    err = GlobusAPIError(res.r)
    assert err._get_args() == [
        res.method,
        res.url,
        None,
        "400",
        "Error",
        '["foo", "bar"]',
    ]


def test_info_is_falsey_on_non_dict_json(make_json_response):
    res = make_json_response(["foo", "bar"], 400)
    err = GlobusAPIError(res.r)
    assert bool(err.info.consent_required) is False
    assert bool(err.info.authorization_parameters) is False
    assert str(err.info) == "AuthorizationParameterInfo(:)|ConsentRequiredInfo(:)"


def test_consent_required_info(make_json_response):
    res = make_json_response(
        {"code": "ConsentRequired", "required_scopes": ["foo", "bar"]}, 401
    )
    err = GlobusAPIError(res.r)
    assert bool(err.info.consent_required) is True
    assert err.info.consent_required.required_scopes == ["foo", "bar"]
    assert str(err.info.consent_required) == (
        "ConsentRequiredInfo(required_scopes=['foo', 'bar'])"
    )

    # if the code is right but the scope list is missing, it should be falsey
    res = make_json_response({"code": "ConsentRequired"}, 401)
    err = GlobusAPIError(res.r)
    assert bool(err.info.consent_required) is False
    assert err.info.consent_required.required_scopes is None
    assert str(err.info.consent_required) == "ConsentRequiredInfo(:)"


def test_authz_params_info_containing_session_message(make_json_response):
    res = make_json_response(
        {"authorization_parameters": {"session_message": "foo"}}, 401
    )
    err = GlobusAPIError(res.r)
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


def test_authz_params_info_containing_session_required_identities(make_json_response):
    res = make_json_response(
        {"authorization_parameters": {"session_required_identities": ["foo", "bar"]}},
        401,
    )
    err = GlobusAPIError(res.r)
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


def test_authz_params_info_containing_session_required_single_domain(
    make_json_response,
):
    res = make_json_response(
        {
            "authorization_parameters": {
                "session_required_single_domain": ["foo", "bar"]
            }
        },
        401,
    )
    err = GlobusAPIError(res.r)
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


def test_authz_params_info_containing_session_required_policies(make_json_response):
    res = make_json_response(
        {"authorization_parameters": {"session_required_policies": "foo,bar"}}, 401
    )
    err = GlobusAPIError(res.r)
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


def test_authz_params_info_containing_malformed_session_required_policies(
    make_json_response,
):
    # confirm that if `session_required_policies` is not a string,
    # it will parse as `None`
    res = make_json_response(
        {"authorization_parameters": {"session_required_policies": ["foo"]}}, 401
    )
    err = GlobusAPIError(res.r)
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
        (500, "Internal Server Error"),
    ],
)
def test_http_reason_exposure(make_response, status, expect_reason):
    res = make_response(
        {"errors": [{"message": "json error message", "code": "Json Error"}]},
        status,
        data_transform=json.dumps,
        headers={"Content-Type": "application/json"},
    )
    err = GlobusAPIError(res.r)
    assert err.http_reason == expect_reason


def test_http_header_exposure(make_response):
    res = make_response(
        {"errors": [{"message": "json error message", "code": "Json Error"}]},
        400,
        data_transform=json.dumps,
        headers={"Content-Type": "application/json", "Spam": "Eggs"},
    )
    err = GlobusAPIError(res.r)
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
    make_response,
    http_method,
    http_status,
    authz_scheme,
    request_url,
    error_code,
    error_message,
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
    request_headers = {}
    if authz_scheme is not None:
        request_headers["Authorization"] = f"{authz_scheme} TOKENINFO"

    # build the response -> error -> error repr
    res = make_response(
        body,
        http_status,
        method=http_method,
        data_transform=json.dumps,
        url=request_url,
        headers=headers,
        request_headers=request_headers,
    )
    err = GlobusAPIError(res.r)
    stringified = repr(err)

    # check using substring -- do not check exact format
    assert http_method in stringified
    assert request_url in stringified
    if authz_scheme in GlobusAPIError.RECOGNIZED_AUTHZ_SCHEMES:
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
