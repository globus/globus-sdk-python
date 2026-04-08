import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

BOOKMARK_ID = str(uuid.uuid4())


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="transfer",
        method="DELETE",
        path=f"/v2/bookmarks/{BOOKMARK_ID}",
        status=200,
        json={"meta": {"request_id": "nH45vUMpD"}},
        metadata={
            "bookmark_id": BOOKMARK_ID,
        },
    )
)
