import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

TUNNEL_ID = str(uuid.uuid4())

GET_TUNNEL_EVENTS_DOC = {
    "data": [
        {
            "type": "TunnelEvent",
            "id": 2768,
            "attributes": {
                "code": "STARTED",
                "is_error": False,
                "description": "started",
                "details": "Attempting tunnel establishment",
                "time": "2026-02-12T21:59:01.857473",
            },
        },
        {
            "type": "TunnelEvent",
            "id": 2769,
            "attributes": {
                "code": "TUNNEL_ACTIVE",
                "is_error": False,
                "description": "tunnel is active",
                "details": "Tunnel has been established",
                "time": "2026-02-12T21:59:02.876253",
            },
        },
        {
            "type": "TunnelEvent",
            "id": 2777,
            "attributes": {
                "code": "TUNNEL_STOPPED",
                "is_error": False,
                "description": "tunnel has been stopped",
                "details": "Tunnel stopped as requested.",
                "time": "2026-02-12T22:12:03.655877",
            },
        },
    ],
    "links": None,
    "meta": {"request_id": "655TZe5vm"},
}


RESPONSES = ResponseSet(
    metadata={
        "tunnel_id": TUNNEL_ID,
    },
    default=RegisteredResponse(
        service="transfer",
        path=f"/v2/tunnels/{TUNNEL_ID}/events",
        json=GET_TUNNEL_EVENTS_DOC,
        method="GET",
    ),
)
