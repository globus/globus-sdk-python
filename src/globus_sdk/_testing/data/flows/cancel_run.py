import copy

from globus_sdk._testing import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_RUN

RUN_ID = TWO_HOP_TRANSFER_RUN["run_id"]
SUCCESS_RESPONSE = copy.deepcopy(TWO_HOP_TRANSFER_RUN)
SUCCESS_RESPONSE.update(
    {
        "status": "FAILED",
        "display_status": "FAILED",
        "details": {
            "time": "2023-06-12T23:04:42.121000+00:00",
            "code": "FlowCanceled",
            "description": "The Flow Instance was canceled by the user",
            "details": {},
        },
    }
)

RESPONSES = ResponseSet(
    metadata={"run_id": RUN_ID},
    default=RegisteredResponse(
        service="flows",
        method="POST",
        path=f"/runs/{RUN_ID}/cancel",
        json=SUCCESS_RESPONSE,
    ),
)
