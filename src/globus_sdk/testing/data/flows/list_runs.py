from __future__ import annotations

import copy
import datetime
import typing as t
import uuid

from responses import matchers

from globus_sdk._testing import RegisteredResponse, ResponseList, ResponseSet

from ._common import RUN, RUN_ID, USER1

FLOW_ID_ALPHA = str(uuid.uuid1())
FLOW_ID_BETA = str(uuid.uuid1())


def generate_example_run(n: int, flow_id: str | None = None) -> dict[str, t.Any]:
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
    if flow_id is not None:
        run_doc["flow_id"] = flow_id

    return run_doc


_combined_filter_output = {
    "runs": [generate_example_run(i, flow_id=FLOW_ID_ALPHA) for i in range(5)]
    + [generate_example_run(i, flow_id=FLOW_ID_BETA) for i in range(5)],
    "limit": 10,
    "has_next_page": False,
}


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
    filter_flow_id=ResponseList(
        RegisteredResponse(
            service="flows",
            path="/runs",
            json={
                "runs": [
                    generate_example_run(i, flow_id=FLOW_ID_ALPHA) for i in range(5)
                ],
                "limit": 5,
                "has_next_page": False,
            },
            match=[matchers.query_param_matcher({"filter_flow_id": FLOW_ID_ALPHA})],
        ),
        RegisteredResponse(
            service="flows",
            path="/runs",
            json={
                "runs": [
                    generate_example_run(i, flow_id=FLOW_ID_BETA) for i in range(5)
                ],
                "limit": 5,
                "has_next_page": False,
            },
            match=[matchers.query_param_matcher({"filter_flow_id": FLOW_ID_BETA})],
        ),
        # register this twice to make the matching order insensitive
        RegisteredResponse(
            service="flows",
            path="/runs",
            json=_combined_filter_output,
            match=[
                matchers.query_param_matcher(
                    {"filter_flow_id": f"{FLOW_ID_ALPHA},{FLOW_ID_BETA}"}
                )
            ],
        ),
        RegisteredResponse(
            service="flows",
            path="/runs",
            json=_combined_filter_output,
            match=[
                matchers.query_param_matcher(
                    {"filter_flow_id": f"{FLOW_ID_BETA},{FLOW_ID_ALPHA}"}
                )
            ],
        ),
        metadata={
            "by_flow_id": {
                FLOW_ID_ALPHA: {
                    "num": 5,
                },
                FLOW_ID_BETA: {
                    "num": 5,
                },
            }
        },
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
