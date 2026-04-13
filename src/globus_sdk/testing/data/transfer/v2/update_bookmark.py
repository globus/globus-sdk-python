import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

BOOKMARK_ID = str(uuid.uuid4())

_collection_id = str(uuid.uuid4())
_name = "private datasets"
_path = "/data_repository/private"
_pinned = True


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="transfer",
        method="PATCH",
        path=f"/v2/bookmarks/{BOOKMARK_ID}",
        status=200,
        json={
            "meta": {"request_id": "dDaKboC8I"},
            "data": {
                "type": "Bookmark",
                "id": BOOKMARK_ID,
                "attributes": {
                    "name": _name,
                    "path": _path,
                    "pinned": _pinned,
                },
                "relationships": {
                    "collection": {
                        "data": {
                            "type": "Collection",
                            "id": _collection_id,
                        }
                    }
                },
            },
        },
        metadata={
            "bookmark_id": BOOKMARK_ID,
            "collection": _collection_id,
            "name": _name,
            "path": _path,
            "pinned": _pinned,
        },
    )
)
