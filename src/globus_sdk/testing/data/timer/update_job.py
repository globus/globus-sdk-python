from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TIMER_ID, V1_TIMER

UPDATED_NAME = "updated name"
UPDATED_TIMER = dict(V1_TIMER)
UPDATED_TIMER["name"] = UPDATED_NAME  # mypy complains if this is onelinerized

RESPONSES = ResponseSet(
    metadata={"job_id": TIMER_ID, "name": UPDATED_NAME},
    default=RegisteredResponse(
        service="timer",
        path=f"/jobs/{TIMER_ID}",
        method="PATCH",
        json=UPDATED_TIMER,
    ),
)
