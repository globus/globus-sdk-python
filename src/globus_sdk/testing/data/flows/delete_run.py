import copy

from globus_sdk._testing import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_RUN

RUN_ID = TWO_HOP_TRANSFER_RUN["run_id"]

SUCCESSFUL_DELETE_RESPONSE = copy.deepcopy(TWO_HOP_TRANSFER_RUN)
SUCCESSFUL_DELETE_RESPONSE.update(
    {
        "status": "SUCCEEDED",
        "display_status": "SUCCEEDED",
        "details": {
            "code": "FlowSucceeded",
            "output": {},
            "description": "The Flow run reached a successful completion state",
        },
    }
)

CONFLICT_RESPONSE = {
    "error": {
        "code": "STATE_CONFLICT",
        "detail": (
            f"Run {RUN_ID} has status 'ACTIVE' but must have status"
            f" in {{'ENDED', 'SUCCEEDED', 'FAILED'}} for requested operation"
        ),
    },
    "debug_id": "80d920b6-66cf-4254-bcbd-7d3efe814e1a",
}

RESPONSES = ResponseSet(
    metadata={"run_id": RUN_ID},
    default=RegisteredResponse(
        service="flows",
        method="POST",
        path=f"/runs/{RUN_ID}/release",
        json=SUCCESSFUL_DELETE_RESPONSE,
    ),
    conflict=RegisteredResponse(
        service="flows",
        method="POST",
        path=f"/runs/{RUN_ID}/release",
        status=409,
        json=CONFLICT_RESPONSE,
    ),
)
