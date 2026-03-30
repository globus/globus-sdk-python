import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

TUNNEL_ID = str(uuid.uuid4())

_initiator_ap = str(uuid.uuid4())
_listener_ap = str(uuid.uuid4())


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="transfer",
        method="GET",
        path=f"/v2/tunnels/{TUNNEL_ID}",
        json={
            "data": {
                "attributes": {
                    "created_time": "2025-12-12T21:11:50.525278",
                    "initiator_ip_address": None,
                    "initiator_port": None,
                    "label": "Buzz Tester",
                    "lifetime_mins": 360,
                    "listener_ip_address": None,
                    "listener_port": None,
                    "restartable": False,
                    "state": "AWAITING_LISTENER",
                    "status": "The tunnel is waiting for listening",
                    "submission_id": "292b0054-7084-46eb-83d6-7a6821b1f77e",
                },
                "id": TUNNEL_ID,
                "relationships": {
                    "initiator": {
                        "data": {"id": _initiator_ap, "type": "StreamAccessPoint"}
                    },
                    "listener": {
                        "data": {"id": _listener_ap, "type": "StreamAccessPoint"}
                    },
                    "owner": {
                        "data": {
                            "id": "4d443580-012d-4954-816f-e0592bd356e1",
                            "type": "Identity",
                        }
                    },
                },
                "type": "Tunnel",
            },
            "meta": {"request_id": "M6kFaS949"},
        },
        metadata={
            "tunnel_id": TUNNEL_ID,
            "initiator_ap": _initiator_ap,
            "listener_ap": _listener_ap,
        },
    ),
)
