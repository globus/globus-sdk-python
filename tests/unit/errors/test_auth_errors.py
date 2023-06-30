import pytest

from globus_sdk import AuthAPIError
from globus_sdk._testing import construct_error


def test_auth_error_get_args_simple():
    err = construct_error(
        error_class=AuthAPIError,
        http_status=404,
        body={"detail": "simple auth error message"},
    )
    req = err._underlying_response.request

    assert err._get_args() == [
        req.method,
        req.url,
        None,
        404,
        "Error",
        "simple auth error message",
    ]


def test_nested_auth_error_message_and_code():
    err = construct_error(
        error_class=AuthAPIError,
        http_status=404,
        body={
            "errors": [
                {"detail": "nested auth error message", "code": "Auth Error"},
                {
                    "title": "some secondary error",
                    "code": "HiddenError",
                },
            ]
        },
    )

    assert err.message == "nested auth error message; some secondary error"
    assert err.code == "Error"


@pytest.mark.parametrize(
    "error_body, expected_error_id",
    (
        (
            {
                "errors": [
                    {"id": "foo"},
                ]
            },
            "foo",
        ),
        (
            {
                "errors": [
                    {"id": "foo"},
                    {"id": "bar"},
                ]
            },
            None,
        ),
        (
            {
                "errors": [
                    {"id": "foo"},
                    {"id": "foo"},
                ]
            },
            "foo",
        ),
        (
            {"errors": [{"id": "foo"}, {"id": "foo"}, {}]},
            "foo",
        ),
    ),
)
def test_auth_error_parses_error_id(error_body, expected_error_id):
    err = construct_error(
        error_class=AuthAPIError,
        http_status=404,
        body=error_body,
    )
    assert err.request_id == expected_error_id
