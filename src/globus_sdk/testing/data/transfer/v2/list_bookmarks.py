import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

_bookmarks = [
    {
        "bookmark_id": str(uuid.uuid4()),
        "collection_id": str(uuid.uuid4()),
        "name": "public datasets",
        "path": "/data_repository/public",
    },
    {
        "bookmark_id": str(uuid.uuid4()),
        "collection_id": str(uuid.uuid4()),
        "name": "private datasets",
        "path": "/data_repository/private",
    },
]

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="transfer",
        method="GET",
        path="/v2/bookmarks",
        json={
            "data": [
                {
                    "type": "Bookmark",
                    "id": b["bookmark_id"],
                    "attributes": {
                        "name": b["name"],
                        "path": b["path"],
                    },
                    "relationships": {
                        "collection": {
                            "data": {
                                "type": "Collection",
                                "id": b["collection_id"],
                            }
                        }
                    },
                }
                for b in _bookmarks
            ],
            "meta": {
                "request_id": "xj8AWyQr8",
            },
            "included": [
                {
                    "type": "Collection",
                    "id": b["collection_id"],
                    "attributes": {
                        "display_name": "Wotsomatta U Dataset Collection",
                        "high_assurance": False,
                    },
                }
                for b in _bookmarks
            ],
        },
    ),
    metadata={"bookmarks": _bookmarks},
)
