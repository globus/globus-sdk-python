import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

TUNNEL_ID = str(uuid.uuid4())

_initiator_ap = str(uuid.uuid4())
_listener_ap = str(uuid.uuid4())

_default_display_name = "Test Tunnel"


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="transfer",
        method="POST",
        path="/v2/tunnels",
        json={
            "data": {
                "attributes": {
                    "created_time": "2025-12-12T21:49:22.183977",
                    "initiator_ip_address": None,
                    "initiator_port": None,
                    "label": _default_display_name,
                    "lifetime_mins": 10,
                    "listener_ip_address": None,
                    "listener_port": None,
                    "restartable": False,
                    "state": "AWAITING_LISTENER",
                    "status": "The tunnel is waiting for listening.",
                    "submission_id": "6ab42cda-d7a4-11f0-ad34-0affc202d2e9",
                },
                "id": "34d97133-f17e-4f90-ad42-56ff5f3c2550",
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
            "meta": {"request_id": "e6KkKkNmw"},
        },
        metadata={
            "tunnel_id": TUNNEL_ID,
            "display_name": _default_display_name,
            "initiator_ap": _initiator_ap,
            "listener_ap": _listener_ap,
        },
    ),
)
