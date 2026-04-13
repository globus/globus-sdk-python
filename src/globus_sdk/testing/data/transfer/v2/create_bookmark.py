import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

BOOKMARK_ID = str(uuid.uuid4())

_collection_id = str(uuid.uuid4())
_name = "public datasets"
_path = "/data_repository/public"


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="transfer",
        method="POST",
        path="/v2/bookmarks",
        status=201,
        json={
            "meta": {"request_id": "nDZoeEMPI"},
            "data": {
                "type": "Bookmark",
                "id": BOOKMARK_ID,
                "attributes": {
                    "name": _name,
                    "path": _path,
                    "pinned": False,
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
        },
    )
)
