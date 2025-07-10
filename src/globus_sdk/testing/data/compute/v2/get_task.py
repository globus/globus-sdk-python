from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import TASK_DOC, TASK_ID

RESPONSES = ResponseSet(
    metadata={"task_id": TASK_ID},
    default=RegisteredResponse(
        service="compute",
        path=f"/v2/tasks/{TASK_ID}",
        method="GET",
        json=TASK_DOC,
    ),
)
