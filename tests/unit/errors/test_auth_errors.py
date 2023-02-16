import pytest

from globus_sdk import AuthAPIError


@pytest.fixture
def simple_auth_response(make_json_response):
    auth_data = {"detail": "simple auth error message"}
    return make_json_response(auth_data, 404)


@pytest.fixture
def nested_auth_response(make_json_response):
    auth_data = {
        "errors": [
            {"detail": "nested auth error message", "code": "Auth Error"},
            {
                "title": "some other error which will not be seen",
                "code": "HiddenError",
            },
        ]
    }
    return make_json_response(auth_data, 404)


@pytest.mark.parametrize(
    "response_fixture_name, status, code, message",
    (
        # normal auth error data
        ("simple_auth_response", "404", "Error", "simple auth error message"),
        ("nested_auth_response", "404", "Auth Error", "nested auth error message"),
        # wrong format (but still parseable)
        ("default_json_response", "400", "Json Error", "json error message"),
        # defaults for non-json data
        ("default_text_response", "401", "Error", "error message"),
        # malformed data is at least rendered successully into an error
        ("malformed_response", "403", "Error", "{"),
    ),
)
def test_get_args_auth(request, response_fixture_name, status, code, message):
    response = request.getfixturevalue(response_fixture_name)

    err = AuthAPIError(response.r)
    assert err._get_args() == [
        response.method,
        response.url,
        None,
        status,
        code,
        message,
    ]
