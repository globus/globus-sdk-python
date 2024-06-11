import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

endpoint_client_id = str(uuid.uuid4())
domain_name = "abc.xyz.data.globus.org"
gcs_manager_url = RegisteredResponse._url_map["gcs"]

RESPONSES = ResponseSet(
    metadata={
        "endpoint_client_id": endpoint_client_id,
        "domain_name": domain_name,
    },
    default=RegisteredResponse(
        service="gcs",
        path="/info",
        json={
            "DATA_TYPE": "result#1.1.0",
            "code": "success",
            "data": [
                {
                    "DATA_TYPE": "info#1.0.0",
                    "api_version": "1.29.0",
                    "client_id": endpoint_client_id,
                    "domain_name": domain_name,
                    "endpoint_id": endpoint_client_id,
                    "manager_version": "5.4.76-rc3",
                },
                {
                    "DATA_TYPE": "connector#1.1.0",
                    "display_name": "POSIX",
                    "id": "145812c8-decc-41f1-83cf-bb2a85a2a70b",
                    "is_baa": False,
                    "is_ha": False,
                },
            ],
        },
    ),
)
