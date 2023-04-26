from globus_sdk._testing import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_RUN

FLOW_ID = TWO_HOP_TRANSFER_RUN["flow_id"]
RUN_ID = TWO_HOP_TRANSFER_RUN["run_id"]
RESPONSES = ResponseSet(
    metadata={"run_id": RUN_ID, "flow_id": FLOW_ID},
    default=RegisteredResponse(
        service="flows",
        method="POST",
        path=f"/runs/{RUN_ID}/resume",
        json=TWO_HOP_TRANSFER_RUN,
    ),
)
