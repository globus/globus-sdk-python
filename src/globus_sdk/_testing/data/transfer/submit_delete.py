from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import SUBMISSION_ID, TASK_ID

RESPONSES = ResponseSet(
    metadata={"submission_id": SUBMISSION_ID, "task_id": TASK_ID},
    default=RegisteredResponse(
        service="transfer",
        method="POST",
        path="/delete",
        json={
            "DATA_TYPE": "delete_result",
            "code": "Accepted",
            "message": (
                "The delete has been accepted and a task has been created "
                "and queued for execution"
            ),
            "request_id": "NS2QXhLZ7",
            "resource": "/delete",
            "submission_id": SUBMISSION_ID,
            "task_id": TASK_ID,
            "task_link": {
                "DATA_TYPE": "link",
                "href": f"task/{TASK_ID}?format=json",
                "rel": "related",
                "resource": "task",
                "title": "related task",
            },
        },
    ),
)
