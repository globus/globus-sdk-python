import itertools
import json

import pytest
import requests

from globus_sdk import ErrorSubdocument, GlobusAPIError, RemovedInV4Warning, exc


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
        "Unauthorized",
    ]
    err = GlobusAPIError(malformed_response.r)
    assert err._get_args() == [
        default_text_response.method,
        default_text_response.url,
        None,
        "403",
        "Error",
        "Forbidden",
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
        "Bad Request",
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
        "Bad Request",
    ]


def test_info_is_falsey_on_non_dict_json(make_json_response):
    res = make_json_response(["foo", "bar"], 400)
    err = GlobusAPIError(res.r)
    assert bool(err.info.consent_required) is False
    assert bool(err.info.authorization_parameters) is False
    assert str(err.info) == "AuthorizationParameterInfo(:)|ConsentRequiredInfo(:)"


@pytest.mark.parametrize(
    "body, is_detected, required_scopes",
    (
        (
            {"code": "ConsentRequired", "required_scopes": ["foo", "bar"]},
            True,
            ["foo", "bar"],
        ),
        (
            {"code": "ConsentRequired", "required_scope": "foo bar"},
            True,
            ["foo bar"],
        ),
        ({"code": "ConsentRequired"}, False, None),
        ({"code": "ConsentRequired", "required_scopes": []}, False, None),
        ({"code": "ConsentRequired", "required_scopes": ["foo", 123]}, False, None),
        ({"code": "ConsentRequired", "required_scope": 1}, False, None),
    ),
)
def test_consent_required_info(make_json_response, body, is_detected, required_scopes):
    res = make_json_response(body, 403)
    err = GlobusAPIError(res.r)

    if is_detected:
        assert bool(err.info.consent_required) is True
        assert err.info.consent_required.required_scopes == required_scopes
    else:
        assert bool(err.info.consent_required) is False


def test_consent_required_info_str(make_json_response):
    info = exc.ConsentRequiredInfo(
        {"code": "ConsentRequired", "required_scopes": ["foo", "bar"]}
    )
    assert str(info) == "ConsentRequiredInfo(required_scopes=['foo', 'bar'])"

    info = exc.ConsentRequiredInfo({})
    assert str(info) == "ConsentRequiredInfo(:)"


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


def test_authz_params_info_containing_malformed_session_message(make_json_response):
    res = make_json_response(
        {"authorization_parameters": {"session_message": 100}}, 401
    )
    err = GlobusAPIError(res.r)
    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_message is None
    assert err.info.authorization_parameters.session_required_identities is None
    assert err.info.authorization_parameters.session_required_single_domain is None
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


def test_authz_params_info_containing_malformed_session_required_identities(
    make_json_response,
):
    res = make_json_response(
        {"authorization_parameters": {"session_required_identities": "foo,bar"}},
        401,
    )
    err = GlobusAPIError(res.r)
    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_message is None
    assert err.info.authorization_parameters.session_required_identities is None
    assert err.info.authorization_parameters.session_required_single_domain is None
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


def test_authz_params_info_containing_malformed_session_required_single_domain(
    make_json_response,
):
    res = make_json_response(
        {"authorization_parameters": {"session_required_single_domain": "foo,bar"}},
        401,
    )
    err = GlobusAPIError(res.r)
    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_message is None
    assert err.info.authorization_parameters.session_required_identities is None
    assert err.info.authorization_parameters.session_required_single_domain is None
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


@pytest.mark.parametrize("policies_value", ["foo,bar", ["foo", "bar"]])
def test_authz_params_info_containing_session_required_policies(
    make_json_response, policies_value
):
    res = make_json_response(
        {"authorization_parameters": {"session_required_policies": policies_value}}, 401
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
        {"authorization_parameters": {"session_required_policies": {"foo": "bar"}}}, 401
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
        ("PUT", 501, None, "https://bogus.example.org/bar", "Not Implemented", None),
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


@pytest.mark.parametrize(
    "content_type",
    ("application/json", "application/unknown+json", "application/vnd.api+json"),
)
def test_loads_jsonapi_error_subdocuments(make_response, content_type):
    res = make_response(
        {
            "errors": [
                {
                    "code": "TooShort",
                    "title": "Password data too short",
                    "detail": "password was only 3 chars long, must be at least 8",
                },
                {
                    "code": "MissingSpecial",
                    "title": "Password data missing special chars",
                    "detail": "password must have non-alphanumeric characters",
                },
                {
                    "code": "ContainsCommonDogName",
                    "title": "Password data has a popular dog name",
                    "detail": "password cannot contain 'spot', 'woofy', or 'clifford'",
                },
            ]
        },
        422,
        data_transform=json.dumps,
        headers={"Content-Type": content_type},
    )
    err = GlobusAPIError(res.r)

    # code is not taken from any of the subdocuments (inherently too ambiguous)
    # behavior will depend on which parsing path was taken
    if content_type.endswith("vnd.api+json"):
        # code becomes None because we saw "true" JSON:API and can opt-in to
        # better behavior
        assert err.code is None
    else:
        # code remains 'Error' for backwards compatibility in the non-JSON:API case
        assert err.code == "Error"

    # but messages can be extracted, and they prefer detail to title
    assert err.messages == [
        "password was only 3 chars long, must be at least 8",
        "password must have non-alphanumeric characters",
        "password cannot contain 'spot', 'woofy', or 'clifford'",
    ]


@pytest.mark.parametrize(
    "content_type",
    ("application/json", "application/unknown+json", "application/vnd.api+json"),
)
def test_loads_jsonapi_error_subdocuments_with_common_code(make_response, content_type):
    res = make_response(
        {
            "errors": [
                {
                    "code": "MissingClass",
                    "title": "Must contain capital letter",
                    "detail": "password must contain at least one capital letter",
                },
                {
                    "code": "MissingClass",
                    "title": "Must contain special chars",
                    "detail": "password must have non-alphanumeric characters",
                },
            ]
        },
        422,
        data_transform=json.dumps,
        headers={"Content-Type": content_type},
    )
    err = GlobusAPIError(res.r)
    # code is taken because all subdocuments have the same code
    assert err.code == "MissingClass"


@pytest.mark.parametrize(
    "content_type",
    ("application/json", "application/unknown+json", "application/vnd.api+json"),
)
def test_loads_jsonapi_error_messages_from_various_fields(make_response, content_type):
    res = make_response(
        {
            "errors": [
                {
                    "message": "invalid password value",
                },
                {
                    "title": "Must contain capital letter",
                },
                {
                    "detail": "password must have non-alphanumeric characters",
                },
            ]
        },
        422,
        data_transform=json.dumps,
        headers={"Content-Type": content_type},
    )
    err = GlobusAPIError(res.r)
    # messages are extracted, and they use whichever field is appropriate for
    # each sub-error
    # note that 'message' will *not* be extracted if the Content-Type indicated JSON:API
    # because JSON:API does not define such a field
    if content_type.endswith("vnd.api+json"):
        # code becomes None because we saw "true" JSON:API and can opt-in to
        # better behavior
        assert err.code is None
        assert err.messages == [
            "Must contain capital letter",
            "password must have non-alphanumeric characters",
        ]
    else:
        # code remains 'Error' for backwards compatibility in the non-JSON:API case
        assert err.code == "Error"

        assert err.messages == [
            "invalid password value",
            "Must contain capital letter",
            "password must have non-alphanumeric characters",
        ]


@pytest.mark.parametrize(
    "error_doc",
    (
        # Type Zero Error Format
        {"code": "FooCode", "message": "FooMessage"},
        # Undefined Error Format
        {"message": "FooMessage"},
    ),
)
def test_non_jsonapi_parsing_uses_root_as_errors_array_by_default(
    make_response, error_doc
):
    res = make_response(
        error_doc,
        422,
        data_transform=json.dumps,
        headers={"Content-Type": "application/json"},
    )
    err = GlobusAPIError(res.r)

    # errors is the doc root wrapped in a list, but converted to a subdocument error
    assert len(err.errors) == 1
    subdoc = err.errors[0]
    assert isinstance(subdoc, ErrorSubdocument)
    assert subdoc.raw == error_doc
    # note that 'message' is supported for error message extraction
    # vs 'detail' and 'title' for JSON:API data
    assert subdoc.message == error_doc["message"]


@pytest.mark.parametrize(
    "error_doc",
    (
        # Type Zero Error Format with sub-error data
        {"code": "FooCode", "message": "FooMessage", "errors": [{"bar": "baz"}]},
        # Type Zero Error Format with *empty* sub-error data
        {"code": "FooCode", "message": "FooMessage", "errors": []},
        # Undefined Error Format with sub-error data
        {"message": "FooMessage", "errors": [{"bar": "baz"}]},
        # Undefined Error Format with *empty* sub-error data
        {"message": "FooMessage", "errors": []},
    ),
)
def test_non_jsonapi_parsing_uses_errors_array_if_present(make_response, error_doc):
    res = make_response(
        error_doc,
        422,
        data_transform=json.dumps,
        headers={"Content-Type": "application/json"},
    )
    err = GlobusAPIError(res.r)

    # errors is the 'errors' list converted to error subdocs
    # first some sanity checks...
    assert len(err.errors) == len(error_doc["errors"])
    assert all(isinstance(subdoc, ErrorSubdocument) for subdoc in err.errors)
    # ...and then a true equivalence test
    assert [e.raw for e in err.errors] == error_doc["errors"]
