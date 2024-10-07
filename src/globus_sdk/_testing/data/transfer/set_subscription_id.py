import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import ENDPOINT_ID, SUBSCRIPTION_ID

OTHER_SUBSCRIPTION_ID = str(uuid.UUID(int=10))

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="transfer",
        method="PUT",
        path=f"/endpoint/{ENDPOINT_ID}/subscription",
        json={
            "DATA_TYPE": "result",
            "code": "Updated",
            "message": "Endpoint updated successfully",
            "request_id": "dWTZZe17L",
            "resource": f"/endpoint/{ENDPOINT_ID}/subscription",
        },
    ),
    not_found=RegisteredResponse(
        service="transfer",
        method="PUT",
        path=f"/endpoint/{ENDPOINT_ID}/subscription",
        status=404,
        json={
            "code": "EndpointNotFound",
            "message": f"No such endpoint '{ENDPOINT_ID}'",
            "request_id": "BHI2BHt8N",
            "resource": f"/endpoint/{ENDPOINT_ID}/subscription",
        },
    ),
    multi_subscriber_cannot_use_default=RegisteredResponse(
        service="transfer",
        method="PUT",
        path=f"/endpoint/{ENDPOINT_ID}/subscription",
        status=400,
        json={
            "code": "BadRequest",
            "message": (
                "Please specify the subscription ID to use. "
                "You currently have access to: "
                f"{SUBSCRIPTION_ID}, {OTHER_SUBSCRIPTION_ID}"
            ),
            "request_id": "H1dFNg6QB",
            "resource": f"/endpoint/{ENDPOINT_ID}/subscription",
        },
        metadata={
            "endpoint_id": ENDPOINT_ID,
            "subscription_ids": [SUBSCRIPTION_ID, OTHER_SUBSCRIPTION_ID],
        },
    ),
)
