import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

TASK_ID = str(uuid.uuid4())

RESPONSES = ResponseSet(
    metadata={"task_id": TASK_ID},
    default=RegisteredResponse(
        service="transfer",
        path=f"/v0.10/task/{TASK_ID}/cancel",
        method="POST",
        json={
            "DATA_TYPE": "result",
            "code": "Canceled",
            "message": "The task has been cancelled successfully.",
            "resource": f"/task/{TASK_ID}/cancel",
            "request_id": "ABCdef789",
        },
    ),
)
