import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

INDEX_IDS = [str(uuid.uuid1()), str(uuid.uuid1())]
SUBSCRIPTIONS = [None, str(uuid.uuid1())]


RESPONSES = ResponseSet(
    metadata={"index_ids": INDEX_IDS, "subscription_ids": SUBSCRIPTIONS},
    default=RegisteredResponse(
        service="search",
        path="/v1/index_list",
        json={
            "index_list": [
                {
                    "@datatype": "GSearchIndex",
                    "@version": "2017-09-01",
                    "display_name": "Index of Indexed Awesomeness",
                    "description": "Turbo Awesome",
                    "id": INDEX_IDS[0],
                    "max_size_in_mb": 1,
                    "size_in_mb": 0,
                    "num_subjects": 0,
                    "num_entries": 0,
                    "creation_date": "2038-07-17 16:48:24",
                    "subscription_id": SUBSCRIPTIONS[0],
                    "is_trial": True,
                    "status": "open",
                    "permissions": ["owner"],
                },
                {
                    "@datatype": "GSearchIndex",
                    "@version": "2017-09-01",
                    "display_name": "Catalog of encyclopediae",
                    "description": "Encyclopediae from Britannica to Wikipedia",
                    "id": INDEX_IDS[1],
                    "max_size_in_mb": 100,
                    "size_in_mb": 23,
                    "num_subjects": 1822,
                    "num_entries": 3644,
                    "creation_date": "2470-10-11 20:09:40",
                    "subscription_id": SUBSCRIPTIONS[1],
                    "is_trial": False,
                    "status": "open",
                    "permissions": ["writer"],
                },
            ]
        },
    ),
)
