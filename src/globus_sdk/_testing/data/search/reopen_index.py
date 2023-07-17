import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

INDEX_ID = str(uuid.uuid4())


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="search",
        method="POST",
        path=f"/v1/index/{INDEX_ID}/reopen",
        json={
            "index_id": INDEX_ID,
            "acknowledged": True,
        },
        metadata={"index_id": INDEX_ID},
    )
)
