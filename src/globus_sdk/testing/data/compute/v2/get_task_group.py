from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import TASK_GROUP_ID, TASK_ID, TASK_ID_2

TASK_BATCH_DOC = {
    "taskgroup_id": TASK_GROUP_ID,
    "create_websockets_queue": True,
    "tasks": [
        {"id": TASK_ID, "created_at": "2021-05-05T15:00:00.000000"},
        {"id": TASK_ID_2, "created_at": "2021-05-05T15:01:00.000000"},
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
        path=f"/v2/taskgroup/{TASK_GROUP_ID}",
        method="GET",
        json=TASK_BATCH_DOC,
    ),
)
