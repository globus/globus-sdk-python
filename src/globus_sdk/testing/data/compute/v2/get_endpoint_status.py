from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import ENDPOINT_ID

DEFAULT_RESPONSE_DOC = {
    "status": "online",
    "details": {
        "total_workers": 1,
        "idle_workers": 0,
        "pending_tasks": 0,
        "outstanding_tasks": 0,
        "managers": 1,
    },
}

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="compute",
        path=f"/v2/endpoints/{ENDPOINT_ID}/status",
        method="GET",
        json=DEFAULT_RESPONSE_DOC,
    ),
)
