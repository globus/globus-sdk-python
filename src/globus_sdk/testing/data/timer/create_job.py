from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TIMER_ID, V1_TIMER

RESPONSES = ResponseSet(
    metadata={"job_id": TIMER_ID},
    default=RegisteredResponse(
        service="timer",
        path="/jobs/",
        method="POST",
        json=V1_TIMER,
        status=201,
    ),
    validation_error=RegisteredResponse(
        service="timer",
        path="/jobs/",
        method="POST",
        json={
            "detail": [
                {
                    "loc": ["body", "start"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
                {
                    "loc": ["body", "callback_url"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ]
        },
        metadata={
            "job_id": TIMER_ID,
            "expect_messages": [
                "field required: body.start",
                "field required: body.callback_url",
            ],
        },
        status=422,
    ),
)
