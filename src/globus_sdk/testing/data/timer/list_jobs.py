from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TIMER_ID, V1_TIMER

RESPONSES = ResponseSet(
    metadata={"job_ids": [TIMER_ID]},
    default=RegisteredResponse(
        service="timer",
        path="/jobs/",
        method="GET",
        json={"jobs": [V1_TIMER]},
    ),
)
