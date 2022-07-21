from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import SUBMISSION_ID, TASK_ID

RESPONSES = ResponseSet(
    metadata={"submission_id": SUBMISSION_ID, "task_id": TASK_ID},
    default=RegisteredResponse(
        service="transfer",
        method="POST",
        path="/transfer",
        json={
            "DATA_TYPE": "transfer_result",
            "code": "Accepted",
            "message": (
                "The transfer has been accepted and a task has been created "
                "and queued for execution"
            ),
            "request_id": "7HgMVYazI",
            "resource": "/transfer",
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
    failure=RegisteredResponse(
        service="transfer",
        method="POST",
        path="/transfer",
        json={
            "code": "ClientError.BadRequest.NoTransferItems",
            "message": "A transfer requires at least one item",
            "request_id": "oUAA6Sq2P",
            "resource": "/transfer",
        },
        status=400,
        metadata={
            "request_id": "oUAA6Sq2P",
        },
    ),
)
