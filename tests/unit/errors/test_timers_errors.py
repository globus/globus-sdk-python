from globus_sdk import TimersAPIError
from globus_sdk._testing import construct_error


def test_timer_error_load_simple():
    err = construct_error(
        error_class=TimersAPIError,
        body={"error": {"code": "ERROR", "detail": "Request failed", "status": 500}},
        http_status=500,
    )

    assert err.code == "ERROR"
    assert err.message == "Request failed"


def test_timer_error_load_nested():
    err = construct_error(
        error_class=TimersAPIError,
        body={
            "detail": [
                {
                    "loc": ["body", "start"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["body", "end"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ]
        },
        http_status=422,
    )

    assert err.code is None
    assert err.message == "field required: body.start; field required: body.end"


def test_timer_error_load_unrecognized_format():
    err = construct_error(error_class=TimersAPIError, body={}, http_status=400)
    assert err.code is None
    assert err.message is None
