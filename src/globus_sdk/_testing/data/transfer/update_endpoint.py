from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import ENDPOINT_ID

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="transfer",
        method="PUT",
        path=f"/endpoint/{ENDPOINT_ID}",
        json={
            "DATA_TYPE": "result",
            "code": "Updated",
            "message": "Endpoint updated successfully",
            "request_id": "6aZjzldyM",
            "resource": f"/endpoint/{ENDPOINT_ID}",
        },
    ),
)
