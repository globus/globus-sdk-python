import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

INDEX_ID = str(uuid.uuid4())


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="search",
        method="POST",
        path="/v1/index",
        json={
            "@datatype": "GSearchIndex",
            "@version": "2017-09-01",
            "creation_date": "2021-04-05 15:05:18",
            "display_name": "Awesome Index of Awesomeness",
            "description": "An index so awesome that it simply cannot be described",
            "id": INDEX_ID,
            "is_trial": True,
            "subscription_id": None,
            "max_size_in_mb": 1,
            "num_entries": 0,
            "num_subjects": 0,
            "size_in_mb": 0,
            "status": "open",
        },
        metadata={"index_id": INDEX_ID},
    )
)
