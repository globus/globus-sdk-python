import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

INDEX_ID = str(uuid.uuid1())
TASK_ID = str(uuid.uuid1())


RESPONSES = ResponseSet(
    metadata={"index_id": INDEX_ID, "task_id": TASK_ID},
    default=RegisteredResponse(
        service="search",
        path=f"/v1/index/{INDEX_ID}/batch_delete_by_subject",
        method="POST",
        json={"task_id": TASK_ID},
    ),
)
