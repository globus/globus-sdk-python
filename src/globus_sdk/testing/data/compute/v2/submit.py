from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import TASK_GROUP_ID, TASK_ID, TASK_ID_2

SUBMIT_RESPONSE = {
    "response": "success",
    "task_group_id": TASK_GROUP_ID,
    "results": [
        {
            "status": "success",
            "task_uuid": TASK_ID,
            "http_status_code": 200,
            "reason": None,
        },
        {
            "status": "success",
            "task_uuid": TASK_ID_2,
            "http_status_code": 200,
            "reason": None,
        },
    ],
}

RESPONSES = ResponseSet(
    metadata={
        "task_group_id": TASK_GROUP_ID,
        "task_id": TASK_ID,
        "task_id_2": TASK_ID_2,
    },
    default=RegisteredResponse(
        service="compute",
        path="/v2/submit",
        method="POST",
        json=SUBMIT_RESPONSE,
    ),
)
