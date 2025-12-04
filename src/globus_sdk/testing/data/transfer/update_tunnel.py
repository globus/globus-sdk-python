import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

TUNNEL_ID = str(uuid.uuid4())


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="transfer",
        method="PATCH",
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
                    "state": "STOPPING",
                    "status": "A request to stop tunnel has been received.",
                    "submission_id": "292b0054-7084-46eb-83d6-7a6821b1f77e",
                },
                "id": "1c1be52d-2d4d-4200-b4ad-d75d43eb0d9c",
                "relationships": {
                    "initiator": {
                        "data": {
                            "id": "80583f05-75f3-4825-b8a5-6c3edf0bbc5c",
                            "type": "StreamAccessPoint",
                        }
                    },
                    "listener": {
                        "data": {
                            "id": "dd5fa993-749f-48fb-86cf-f07ad5797d7e",
                            "type": "StreamAccessPoint",
                        }
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
            "meta": {"request_id": "pN0Aact40"},
        },
        metadata={
            "tunnel_id": TUNNEL_ID,
        },
    ),
)
