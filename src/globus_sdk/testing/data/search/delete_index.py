import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

INDEX_ID = str(uuid.uuid4())


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="search",
        method="DELETE",
        path=f"/v1/index/{INDEX_ID}",
        json={
            "index_id": INDEX_ID,
            "acknowledged": True,
        },
        metadata={"index_id": INDEX_ID},
    ),
    delete_pending=RegisteredResponse(
        service="search",
        method="DELETE",
        path=f"/v1/index/{INDEX_ID}",
        status=409,
        json={
            "@datatype": "GError",
            "request_id": "3430ce9a5f9d929ef7682e4c58363dee",
            "status": 409,
            "@version": "2017-09-01",
            "message": (
                "Index status (delete_pending) did not match required status "
                "for this operation: open"
            ),
            "code": "Conflict.IncompatibleIndexStatus",
        },
        metadata={"index_id": INDEX_ID},
    ),
)
