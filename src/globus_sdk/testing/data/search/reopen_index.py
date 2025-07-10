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
    ),
    already_open=RegisteredResponse(
        service="search",
        method="POST",
        path=f"/v1/index/{INDEX_ID}/reopen",
        status=409,
        json={
            "code": "Conflict.IncompatibleIndexStatus",
            "request_id": "e1ad6822156dea372027eee48c16e150",
            "@datatype": "GError",
            "message": (
                "Index status (open) did not match required status for "
                "this operation: delete_pending"
            ),
            "@version": "2017-09-01",
            "status": 409,
        },
        metadata={"index_id": INDEX_ID},
    ),
)
