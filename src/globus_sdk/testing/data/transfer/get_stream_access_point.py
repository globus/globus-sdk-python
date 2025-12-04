import uuid

from globus_sdk.testing.models import RegisteredResponse, ResponseSet

ACCESS_POINT_ID = str(uuid.uuid4())


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="transfer",
        method="GET",
        path=f"/v2/stream_access_points/{ACCESS_POINT_ID}",
        json={
            "data": {
                "attributes": {
                    "advertised_owner": "john@globus.org",
                    "contact_email": None,
                    "contact_info": None,
                    "department": None,
                    "description": None,
                    "display_name": "Buzz Dev Listener",
                    "info_link": None,
                    "keywords": None,
                    "organization": None,
                    "tlsftp_server": (
                        "tlsftp://s-463c7.e7d5e.8540."
                        "test3.zones.dnsteam.globuscs.info:443"
                    ),
                },
                "id": ACCESS_POINT_ID,
                "relationships": {
                    "host_endpoint": {
                        "data": {
                            "id": "d6428474-c308-4a2d-8a86-d377915d978b",
                            "type": "Endpoint",
                        }
                    }
                },
                "type": "StreamAccessPoint",
            },
            "meta": {"request_id": "55QRq2iBa"},
        },
        metadata={
            "access_point_id": ACCESS_POINT_ID,
        },
    ),
)
