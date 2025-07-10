from copy import deepcopy

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_FLOW_DOC, TWO_HOP_TRANSFER_FLOW_ID

_two_hop_transfer_update_request = {
    "subtitle": "Specifically, in two steps",
    "description": "Transfer from source to destination, stopping off at staging",
    "subscription_id": "00000000-3ba7-456e-9df7-fc40028f3331",
}


_updated_two_hop_transfer_flow_doc = deepcopy(TWO_HOP_TRANSFER_FLOW_DOC)
_updated_two_hop_transfer_flow_doc.update(_two_hop_transfer_update_request)


RESPONSES = ResponseSet(
    metadata={
        "flow_id": TWO_HOP_TRANSFER_FLOW_ID,
        "params": _two_hop_transfer_update_request,
    },
    default=RegisteredResponse(
        service="flows",
        path=f"/flows/{TWO_HOP_TRANSFER_FLOW_ID}",
        method="PUT",
        json=_updated_two_hop_transfer_flow_doc,
    ),
)
