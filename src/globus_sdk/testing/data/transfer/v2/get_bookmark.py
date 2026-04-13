import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

BOOKMARK_ID = str(uuid.uuid4())

_collection_id = str(uuid.uuid4())
_name = "public datasets"
_path = "/data_repository/public"


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="transfer",
        method="GET",
        path=f"/v2/bookmarks/{BOOKMARK_ID}",
        json={
            "meta": {"request_id": "HKsv2T65H"},
            "data": {
                "type": "Bookmark",
                "id": BOOKMARK_ID,
                "attributes": {"name": _name, "path": _path, "pinned": True},
                "relationships": {
                    "collection": {
                        "data": {
                            "type": "Collection",
                            "id": _collection_id,
                        }
                    }
                },
            },
            "included": [
                {
                    "type": "Collection",
                    "id": _collection_id,
                    "attributes": {
                        "display_name": "GCP High Assurance Mapped Collection",
                        "high_assurance": True,
                    },
                }
            ],
        },
        metadata={
            "bookmark_id": BOOKMARK_ID,
            "collection": _collection_id,
            "name": _name,
            "path": _path,
        },
    )
)
