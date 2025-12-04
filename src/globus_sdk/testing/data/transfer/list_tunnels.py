from globus_sdk.testing.models import RegisteredResponse, ResponseSet

TUNNEL_LIST_DOC = {
    "data": [
        {
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
                "status": "The tunnel is waiting for listening contact detail setup.",
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
        {
            "attributes": {
                "created_time": "2025-12-12T21:22:11.018233",
                "initiator_ip_address": None,
                "initiator_port": None,
                "label": "part 2",
                "lifetime_mins": 360,
                "listener_ip_address": None,
                "listener_port": None,
                "restartable": False,
                "state": "AWAITING_LISTENER",
                "status": "The tunnel is waiting for listening contact detail setup.",
                "submission_id": "fb3b1220-1d5f-4dcf-92f5-e7056a514319",
            },
            "id": "bf1b0d16-7d93-44eb-8773-9066a750c13e",
            "relationships": {
                "initiator": {
                    "data": {
                        "id": "34c6e671-c011-4bf8-bc30-5ccebada8f3b",
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
    ],
    "links": None,
    "meta": {"request_id": "fAAfpnino"},
}


RESPONSES = ResponseSet(
    metadata={},
    default=RegisteredResponse(
        service="transfer",
        path="/v2/tunnels",
        json=TUNNEL_LIST_DOC,
        method="GET",
    ),
)
