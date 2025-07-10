from __future__ import annotations

import typing as t
import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

INDEX_IDS = [str(uuid.uuid1()), str(uuid.uuid1())]
INDEX_ATTRIBUTES: dict[str, dict[str, t.Any]] = {
    INDEX_IDS[0]: {
        "subscription_id": None,
        "creation_date": "2038-07-17 16:48:24",
        "display_name": "Index of Indexed Awesomeness",
        "description": "Turbo Awesome",
        "max_size_in_mb": 1,
        "size_in_mb": 0,
        "num_subjects": 0,
        "num_entries": 0,
        "permissions": ["owner"],
    },
    INDEX_IDS[1]: {
        "subscription_id": str(uuid.uuid1()),
        "creation_date": "2470-10-11 20:09:40",
        "display_name": "Catalog of encyclopediae",
        "description": "Encyclopediae from Britannica to Wikipedia",
        "max_size_in_mb": 100,
        "size_in_mb": 23,
        "num_subjects": 1822,
        "num_entries": 3644,
        "permissions": ["writer"],
    },
}


def _make_doc(index_id: str) -> dict[str, t.Any]:
    attrs = INDEX_ATTRIBUTES[index_id]
    return {
        "@datatype": "GSearchIndex",
        "@version": "2017-09-01",
        "id": index_id,
        "is_trial": False if attrs["subscription_id"] else True,
        "status": "open",
        **attrs,
    }


RESPONSES = ResponseSet(
    metadata={"index_ids": INDEX_IDS, "index_attributes": INDEX_ATTRIBUTES},
    default=RegisteredResponse(
        service="search",
        path="/v1/index_list",
        json={
            "index_list": [
                _make_doc(INDEX_IDS[0]),
                _make_doc(INDEX_IDS[1]),
            ]
        },
    ),
)
