from __future__ import annotations

import datetime
import typing as t
import uuid

from responses import matchers

from globus_sdk.testing.models import RegisteredResponse, ResponseList, ResponseSet

OWNER_URN = "urn:globus:auth:identity:a1234567-1234-1234-1234-123456789abc"


def generate_registered_api_summary(n: int) -> dict[str, t.Any]:
    """
    Generate a summary registered API object for list responses.

    :param n: The index number used to generate unique IDs and timestamps
    """
    api_id = str(uuid.UUID(int=n))
    base_time = datetime.datetime.fromisoformat("2024-01-01T00:00:00+00:00")
    created_timestamp = base_time + datetime.timedelta(days=n)
    updated_timestamp = created_timestamp + datetime.timedelta(hours=n)

    return {
        "id": api_id,
        "name": f"registered-api-{n}",
        "description": f"Test registered API number {n}",
        "created_timestamp": created_timestamp.isoformat(),
        "updated_timestamp": updated_timestamp.isoformat(),
    }


FIRST_REGISTERED_API_ID = str(uuid.UUID(int=0))

RESPONSES = ResponseSet(
    metadata={"first_registered_api_id": FIRST_REGISTERED_API_ID},
    default=RegisteredResponse(
        service="flows",
        path="/registered_apis",
        json={
            "registered_apis": [generate_registered_api_summary(0)],
            "limit": 1,
            "has_next_page": False,
            "marker": None,
        },
    ),
    paginated=ResponseList(
        RegisteredResponse(
            service="flows",
            path="/registered_apis",
            json={
                "registered_apis": [
                    generate_registered_api_summary(i) for i in range(10)
                ],
                "limit": 10,
                "has_next_page": True,
                "marker": "fake_marker_0",
            },
        ),
        RegisteredResponse(
            service="flows",
            path="/registered_apis",
            json={
                "registered_apis": [
                    generate_registered_api_summary(i) for i in range(10, 20)
                ],
                "limit": 10,
                "has_next_page": True,
                "marker": "fake_marker_1",
            },
            match=[matchers.query_param_matcher({"marker": "fake_marker_0"})],
        ),
        RegisteredResponse(
            service="flows",
            path="/registered_apis",
            json={
                "registered_apis": [
                    generate_registered_api_summary(i) for i in range(20, 25)
                ],
                "limit": 5,
                "has_next_page": False,
                "marker": None,
            },
            match=[matchers.query_param_matcher({"marker": "fake_marker_1"})],
        ),
        metadata={
            "owner_urn": OWNER_URN,
            "num_pages": 3,
            "expect_markers": ["fake_marker_0", "fake_marker_1", None],
            "total_items": 25,
        },
    ),
)
