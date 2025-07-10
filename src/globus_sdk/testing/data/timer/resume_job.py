from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TIMER_ID

RESPONSES = ResponseSet(
    metadata={"job_id": TIMER_ID},
    default=RegisteredResponse(
        service="timer",
        path=f"/jobs/{TIMER_ID}/resume",
        method="POST",
        json={"message": f"Successfully resumed job {TIMER_ID}."},
    ),
)
