from globus_sdk import TransferAPIError
from globus_sdk.testing import construct_error


def test_transfer_response_get_args():
    err = construct_error(
        error_class=TransferAPIError,
        body={
            "message": "transfer error message",
            "code": "Transfer Error",
            "request_id": "123",
        },
        http_status=404,
    )
    req = err._underlying_response.request
    assert err._get_args() == [
        req.method,
        req.url,
        None,
        404,
        "Transfer Error",
        "transfer error message",
        "123",
    ]
