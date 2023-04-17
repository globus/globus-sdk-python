import pytest

from globus_sdk import TransferAPIError


@pytest.fixture
def transfer_response(make_json_response):
    transfer_data = {
        "message": "transfer error message",
        "code": "Transfer Error",
        "request_id": 123,
    }
    return make_json_response(transfer_data, 404)


@pytest.mark.parametrize(
    "response_fixture_name, status, code, message, request_id",
    (
        # normal transfer error data
        ("transfer_response", "404", "Transfer Error", "transfer error message", 123),
        # wrong format (but still parseable)
        ("default_json_response", "400", "Json Error", "json error message", None),
        # defaults for non-json data
        ("default_text_response", "401", "Error", "error message", None),
        # malformed data is at least rendered successfully into an error
        ("malformed_response", "403", "Error", "{", None),
    ),
)
def test_get_args_transfer(
    request, response_fixture_name, status, code, message, request_id
):
    response = request.getfixturevalue(response_fixture_name)
    err = TransferAPIError(response.r)
    assert err._get_args() == [
        response.method,
        response.url,
        None,
        status,
        code,
        message,
        request_id,
    ]
