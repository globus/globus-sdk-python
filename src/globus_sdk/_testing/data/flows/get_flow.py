from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_FLOW_DOC, TWO_HOP_TRANSFER_FLOW_ID

RESPONSES = ResponseSet(
    metadata={
        "flow_id": TWO_HOP_TRANSFER_FLOW_ID,
        "title": TWO_HOP_TRANSFER_FLOW_DOC["title"],
    },
    default=RegisteredResponse(
        service="flows",
        path=f"/flows/{TWO_HOP_TRANSFER_FLOW_ID}",
        json=TWO_HOP_TRANSFER_FLOW_DOC,
    ),
)
