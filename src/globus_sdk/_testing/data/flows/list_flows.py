from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_FLOW_DOC, TWO_HOP_TRANSFER_FLOW_ID

RESPONSES = ResponseSet(
    metadata={"first_flow_id": TWO_HOP_TRANSFER_FLOW_ID},
    default=RegisteredResponse(
        service="flows",
        path="/flows",
        json={
            "flows": [TWO_HOP_TRANSFER_FLOW_DOC],
            "limit": 20,
            "has_next_page": False,
            "marker": None,
        },
    ),
)
