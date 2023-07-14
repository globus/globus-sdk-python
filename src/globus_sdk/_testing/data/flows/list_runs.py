from __future__ import annotations

import copy
import datetime
import typing as t
import uuid

from responses import matchers

from globus_sdk._testing import RegisteredResponse, ResponseList, ResponseSet

from ._common import RUN, RUN_ID, USER1


def generate_example_run(n: int) -> dict[str, t.Any]:
    run_id = str(uuid.UUID(int=n))

    base_time = datetime.datetime.fromisoformat("2021-10-18T19:19:35.967289+00:00")
    start_time = base_time + datetime.timedelta(days=n)
    completion_time = base_time + datetime.timedelta(days=n + 1)

    run_doc = copy.deepcopy(RUN)
    run_doc["completion_time"] = completion_time.isoformat()
    run_doc["label"] = f"Run {n}"
    run_doc["start_time"] = start_time.isoformat()
    run_doc["run_id"] = run_id
    run_doc["action_id"] = run_id

    return run_doc


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="flows",
        path="/runs",
        json={
            "runs": [RUN],
            "limit": 20,
            "has_next_page": False,
            "marker": None,
        },
        metadata={"first_run_id": RUN_ID},
    ),
    paginated=ResponseList(
        RegisteredResponse(
            service="flows",
            path="/runs",
            json={
                "runs": [generate_example_run(i) for i in range(20)],
                "limit": 20,
                "has_next_page": True,
                "marker": "fake_marker_0",
            },
        ),
        RegisteredResponse(
            service="flows",
            path="/runs",
            json={
                "runs": [generate_example_run(i) for i in range(20, 40)],
                "limit": 20,
                "has_next_page": True,
                "marker": "fake_marker_1",
            },
            match=[matchers.query_param_matcher({"marker": "fake_marker_0"})],
        ),
        RegisteredResponse(
            service="flows",
            path="/runs",
            json={
                "runs": [generate_example_run(i) for i in range(40, 60)],
                "limit": 20,
                "has_next_page": False,
                "marker": None,
            },
            match=[matchers.query_param_matcher({"marker": "fake_marker_1"})],
        ),
        metadata={
            "owner_id": USER1,
            "num_pages": 3,
            "expect_markers": ["fake_marker_0", "fake_marker_1", None],
            "total_items": 60,
        },
    ),
)
