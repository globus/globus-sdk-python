import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

_bookmarks = [
    {
        "bookmark_id": str(uuid.uuid4()),
        "collection_id": str(uuid.uuid4()),
        "name": "public datasets",
        "path": "/data_repository/public",
        "pinned": True,
    },
    {
        "bookmark_id": str(uuid.uuid4()),
        "collection_id": str(uuid.uuid4()),
        "name": "private datasets",
        "path": "/data_repository/private",
        "pinned": False,
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
                        "pinned": b["pinned"],
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
