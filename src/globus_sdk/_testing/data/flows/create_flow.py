from responses import matchers

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_FLOW_DOC

_two_hop_transfer_create_request = {
    "title": TWO_HOP_TRANSFER_FLOW_DOC["title"],
    "definition": TWO_HOP_TRANSFER_FLOW_DOC["definition"],
    "input_schema": TWO_HOP_TRANSFER_FLOW_DOC["input_schema"],
    "subtitle": TWO_HOP_TRANSFER_FLOW_DOC["subtitle"],
    "description": TWO_HOP_TRANSFER_FLOW_DOC["description"],
    "flow_viewers": TWO_HOP_TRANSFER_FLOW_DOC["flow_viewers"],
    "flow_starters": TWO_HOP_TRANSFER_FLOW_DOC["flow_starters"],
    "flow_administrators": TWO_HOP_TRANSFER_FLOW_DOC["flow_administrators"],
    "keywords": TWO_HOP_TRANSFER_FLOW_DOC["keywords"],
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
        match=[matchers.json_params_matcher(_two_hop_transfer_create_request)],
    ),
)
