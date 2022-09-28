from responses import matchers

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_FLOW_DOC

_two_hop_transfer_create_request = {
    k: TWO_HOP_TRANSFER_FLOW_DOC[k]
    for k in [
        "title",
        "definition",
        "input_schema",
        "subtitle",
        "description",
        "flow_viewers",
        "flow_starters",
        "flow_administrators",
        "keywords",
    ]
}
RESPONSES = ResponseSet(
    metadata={
        "params": _two_hop_transfer_create_request,
    },
    default=RegisteredResponse(
        service="flows",
        path="/flows",
        method="POST",
        json=TWO_HOP_TRANSFER_FLOW_DOC,
        match=[matchers.json_params_matcher(params=_two_hop_transfer_create_request)],
    ),
)
