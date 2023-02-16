from globus_sdk import TimerAPIError


def test_timer_error_load_simple(make_json_response):
    response = make_json_response(
        {"error": {"code": "ERROR", "detail": "Request failed", "status": 500}},
        500,
    )

    err = TimerAPIError(response.r)
    assert err.code == "ERROR"
    assert err.message == "Request failed"


def test_timer_error_load_nested(make_json_response):
    response = make_json_response(
        {
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
        422,
    )

    err = TimerAPIError(response.r)
    assert err.code == "Validation Error"
    assert err.message == "field required: body.start; field required: body.end"


def test_timer_error_load_unrecognize_format(make_json_response):
    response = make_json_response({}, 400)

    err = TimerAPIError(response.r)
    assert err.code == "Unknown Error"
    assert err.message == "Could not parse error details from the response"
