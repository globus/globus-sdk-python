from responses import matchers

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_FLOW_ID, TWO_HOP_TRANSFER_RUN

_request_params = {
    "body": TWO_HOP_TRANSFER_RUN["details"]["details"]["input"],
    "tags": TWO_HOP_TRANSFER_RUN["tags"],
    "label": TWO_HOP_TRANSFER_RUN["label"],
    "run_monitors": TWO_HOP_TRANSFER_RUN["run_monitors"],
    "run_managers": TWO_HOP_TRANSFER_RUN["run_managers"],
}
RESPONSES = ResponseSet(
    metadata={"flow_id": TWO_HOP_TRANSFER_FLOW_ID, "request_params": _request_params},
    default=RegisteredResponse(
        service="flows",
        method="POST",
        path=f"/flows/{TWO_HOP_TRANSFER_FLOW_ID}/run",
        json=TWO_HOP_TRANSFER_RUN,
        match=[matchers.json_params_matcher(params=_request_params)],
    ),
)
