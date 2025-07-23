import itertools

import pytest
import requests

from globus_sdk import ErrorSubdocument, GlobusAPIError, exc
from globus_sdk.testing import construct_error


def _strmatch_any_order(inputstr, prefix, midfixes, suffix, sep=", "):
    # test for string matching, but without insisting on ordering of middle segments
    assert inputstr in [
        prefix + sep.join(m) + suffix for m in itertools.permutations(midfixes)
    ]


def test_raw_json_property():
    data = {
        "code": "Json Error",
        "errors": [
            {
                "message": "json error message",
                "title": "json error title",
            }
        ],
    }

    err = construct_error(body=data, http_status=400)
    assert err.raw_json == data


@pytest.mark.parametrize(
    "body, response_headers",
    (
        ("text_data", {}),  # plain text
        ("{", {"Content-Type": "application/json"}),  # malformed JSON
    ),
)
def test_raw_json_none_on_nonjson_data(body, response_headers):
    err = construct_error(body=body, response_headers=response_headers, http_status=400)
    assert err.raw_json is None


def test_text_property():
    err = construct_error(body="text_data", http_status=400)
    assert err.text == "text_data"


def test_binary_content_property():
    body_text = "some data"
    err = construct_error(body=body_text, http_status=400)
    assert err.binary_content == body_text.encode("utf-8")


@pytest.mark.parametrize(
    "body, response_headers, http_status, expect_code, expect_message",
    (
        ("text_data", {}, 401, None, "Unauthorized"),  # text
        # JSON with unrecognized contents
        (
            {"foo": "bar"},
            {"Content-Type": "application/json"},
            403,
            None,
            "Forbidden",
        ),
        # JSON with well-known contents
        (
            {"code": "foo", "message": "bar"},
            {"Content-Type": "application/json"},
            403,
            "foo",
            "bar",
        ),
        # non-dict JSON with well-known contents
        (
            "[]",
            {"Content-Type": "application/json"},
            403,
            None,
            "Forbidden",
        ),
        # invalid JSON
        (
            "{",
            {"Content-Type": "application/json"},
            400,
            None,
            "Bad Request",
        ),
    ),
)
def test_get_args(body, response_headers, http_status, expect_code, expect_message):
    err = construct_error(
        body=body, response_headers=response_headers, http_status=http_status
    )
    req = err._underlying_response.request
    assert err._get_args() == [
        req.method,
        req.url,
        None,
        http_status,
        expect_code,
        expect_message,
    ]


def test_info_is_falsey_on_non_dict_json():
    err = construct_error(
        body="[]",
        response_headers={"Content-Type": "application/json"},
        http_status=400,
    )
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
def test_consent_required_info(body, is_detected, required_scopes):
    err = construct_error(body=body, http_status=403)

    if is_detected:
        assert bool(err.info.consent_required) is True
        assert err.info.consent_required.required_scopes == required_scopes
    else:
        assert bool(err.info.consent_required) is False


def test_consent_required_info_str():
    info = exc.ConsentRequiredInfo(
        {"code": "ConsentRequired", "required_scopes": ["foo", "bar"]}
    )
    assert str(info) == "ConsentRequiredInfo(required_scopes=['foo', 'bar'])"

    info = exc.ConsentRequiredInfo({})
    assert str(info) == "ConsentRequiredInfo(:)"


def test_authz_params_info_containing_session_message():
    body = {"authorization_parameters": {"session_message": "foo"}}
    err = construct_error(body=body, http_status=403)

    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_message == "foo"
    assert err.info.authorization_parameters.session_required_identities is None
    assert err.info.authorization_parameters.session_required_single_domain is None
    assert err.info.authorization_parameters.session_required_policies is None
    print("derk")
    print(str(err.info.authorization_parameters))
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=foo",
            "session_required_identities=None",
            "session_required_single_domain=None",
            "session_required_policies=None",
            "session_required_mfa=None",
        ],
        ")",
    )


def test_authz_params_info_containing_malformed_session_message():
    body = {"authorization_parameters": {"session_message": 100}}
    err = construct_error(error_class=GlobusAPIError, body=body, http_status=403)

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
            "session_required_mfa=None",
        ],
        ")",
    )


def test_authz_params_info_containing_session_required_identities():
    body = {"authorization_parameters": {"session_required_identities": ["foo", "bar"]}}
    err = construct_error(body=body, http_status=403)

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
            "session_required_mfa=None",
        ],
        ")",
    )


def test_authz_params_info_containing_malformed_session_required_identities():
    body = {"authorization_parameters": {"session_required_identities": "foo,bar"}}
    err = construct_error(error_class=GlobusAPIError, body=body, http_status=403)

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
            "session_required_mfa=None",
        ],
        ")",
    )


def test_authz_params_info_containing_session_required_single_domain():
    body = {
        "authorization_parameters": {"session_required_single_domain": ["foo", "bar"]}
    }
    err = construct_error(body=body, http_status=403)

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
            "session_required_mfa=None",
        ],
        ")",
    )


def test_authz_params_info_containing_malformed_session_required_single_domain():
    body = {"authorization_parameters": {"session_required_single_domain": "foo,bar"}}
    err = construct_error(body=body, http_status=403)

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
            "session_required_mfa=None",
        ],
        ")",
    )


@pytest.mark.parametrize("policies_value", ["foo,bar", ["foo", "bar"]])
def test_authz_params_info_containing_session_required_policies(policies_value):
    body = {"authorization_parameters": {"session_required_policies": policies_value}}
    err = construct_error(error_class=GlobusAPIError, body=body, http_status=403)
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
            "session_required_mfa=None",
        ],
        ")",
    )


def test_authz_params_info_containing_malformed_session_required_policies():
    # confirm that if `session_required_policies` is not str|list[str],
    # it will parse as `None`
    body = {"authorization_parameters": {"session_required_policies": {"foo": "bar"}}}
    err = construct_error(body=body, http_status=403)

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
            "session_required_mfa=None",
        ],
        ")",
    )


@pytest.mark.parametrize("mfa_value", [True, False])
def test_authz_params_info_containing_session_required_mfa(mfa_value):
    body = {"authorization_parameters": {"session_required_mfa": mfa_value}}
    err = construct_error(body=body, http_status=403)

    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_required_mfa is mfa_value
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=None",
            "session_required_identities=None",
            "session_required_single_domain=None",
            "session_required_policies=None",
            f"session_required_mfa={mfa_value}",
        ],
        ")",
    )


def test_authz_params_info_containing_malformed_session_required_mfa():
    body = {"authorization_parameters": {"session_required_mfa": "foobarjohn"}}
    err = construct_error(body=body, http_status=403)

    assert bool(err.info.authorization_parameters) is True
    assert err.info.authorization_parameters.session_required_mfa is None
    _strmatch_any_order(
        str(err.info.authorization_parameters),
        "AuthorizationParameterInfo(",
        [
            "session_message=None",
            "session_required_identities=None",
            "session_required_single_domain=None",
            "session_required_policies=None",
            "session_required_mfa=None",
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
def test_http_reason_exposure(status, expect_reason):
    body = {"errors": [{"message": "json error message", "code": "Json Error"}]}
    err = construct_error(body=body, http_status=status)
    assert err.http_reason == expect_reason


def test_http_header_exposure(make_response):
    body = {"errors": [{"message": "json error message", "code": "Json Error"}]}
    err = construct_error(
        body=body,
        http_status=400,
        response_headers={"Content-Type": "application/json", "Spam": "Eggs"},
    )
    assert err.headers["Spam"] == "Eggs"
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
    err = construct_error(
        body=body,
        http_status=http_status,
        method=http_method,
        url=request_url,
        response_headers=headers,
        request_headers=request_headers,
    )
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
        # several things could be 'None', but at least one of them is 'code'
        assert "None" in stringified
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
def test_loads_jsonapi_error_subdocuments(content_type):
    body = {
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
    }
    err = construct_error(
        body=body, http_status=422, response_headers={"Content-Type": content_type}
    )

    # code is not taken from any of the subdocuments (inherently too ambiguous)
    # this holds regardless of which parsing path was taken
    assert err.code is None

    # messages can be extracted, and they prefer detail to title
    assert err.messages == [
        "password was only 3 chars long, must be at least 8",
        "password must have non-alphanumeric characters",
        "password cannot contain 'spot', 'woofy', or 'clifford'",
    ]


@pytest.mark.parametrize(
    "content_type",
    ("application/json", "application/unknown+json", "application/vnd.api+json"),
)
def test_loads_jsonapi_error_subdocuments_with_common_code(content_type):
    body = {
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
    }
    err = construct_error(
        body=body, http_status=422, response_headers={"Content-Type": content_type}
    )
    # code is taken because all subdocuments have the same code
    assert err.code == "MissingClass"


@pytest.mark.parametrize(
    "content_type",
    ("application/json", "application/unknown+json", "application/vnd.api+json"),
)
def test_loads_jsonapi_error_messages_from_various_fields(content_type):
    body = {
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
    }
    err = construct_error(
        body=body, http_status=422, response_headers={"Content-Type": content_type}
    )

    # no code was found
    assert err.code is None

    # messages are extracted, and they use whichever field is appropriate for
    # each sub-error
    # note that 'message' will *not* be extracted if the Content-Type indicated JSON:API
    # because JSON:API does not define such a field
    if content_type.endswith("vnd.api+json"):
        assert err.messages == [
            "Must contain capital letter",
            "password must have non-alphanumeric characters",
        ]
    else:
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
def test_non_jsonapi_parsing_uses_root_as_errors_array_by_default(error_doc):
    err = construct_error(body=error_doc, http_status=422)

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
def test_non_jsonapi_parsing_uses_errors_array_if_present(error_doc):
    err = construct_error(body=error_doc, http_status=422)

    # errors is the 'errors' list converted to error subdocs
    # first some sanity checks...
    assert len(err.errors) == len(error_doc["errors"])
    assert all(isinstance(subdoc, ErrorSubdocument) for subdoc in err.errors)
    # ...and then a true equivalence test
    assert [e.raw for e in err.errors] == error_doc["errors"]
