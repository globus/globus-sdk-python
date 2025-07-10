from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TIMER_ID, V1_TIMER

RESPONSES = ResponseSet(
    metadata={"job_id": TIMER_ID},
    default=RegisteredResponse(
        service="timer",
        path=f"/jobs/{TIMER_ID}",
        method="DELETE",
        json=V1_TIMER,
    ),
)
