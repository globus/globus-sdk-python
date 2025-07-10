import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

endpoint_id = str(uuid.uuid4())
gcs_manager_url = RegisteredResponse._url_map["gcs"]
display_name = "Happy Fun Endpoint"

RESPONSES = ResponseSet(
    metadata={
        "endpoint_id": endpoint_id,
        "display_name": display_name,
        "gcs_manager_url": gcs_manager_url,
    },
    default=RegisteredResponse(
        service="gcs",
        method="PATCH",
        path="/endpoint",
        json={
            "DATA_TYPE": "result#1.0.0",
            "code": "success",
            "data": [],
            "detail": "success",
            "has_next_page": False,
            "http_response_code": 200,
            "message": f"Updated endpoint {endpoint_id}",
        },
    ),
    include_endpoint=RegisteredResponse(
        service="gcs",
        method="PATCH",
        path="/endpoint",
        json={
            "DATA_TYPE": "result#1.0.0",
            "code": "success",
            "data": [
                {
                    "DATA_TYPE": "endpoint#1.2.0",
                    "allow_udt": False,
                    "contact_email": "user@globus.org",
                    "display_name": display_name,
                    "gcs_manager_url": gcs_manager_url,
                    "gridftp_control_channel_port": 443,
                    "id": endpoint_id,
                    "network_use": "normal",
                    "organization": "Globus",
                    "public": True,
                    "subscription_id": None,
                }
            ],
            "detail": "success",
            "has_next_page": False,
            "http_response_code": 200,
            "message": f"Updated endpoint {endpoint_id}",
        },
    ),
)
