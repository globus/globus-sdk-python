import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

TUNNEL_ID = str(uuid.uuid4())


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="transfer",
        method="DELETE",
        path=f"/v2/tunnels/{TUNNEL_ID}",
        json={"data": None, "meta": {"request_id": "ofayi2B4R"}},
        metadata={
            "tunnel_id": TUNNEL_ID,
        },
    ),
)
