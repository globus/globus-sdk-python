from globus_sdk._testing.models import RegisteredResponse, ResponseSet

CREDENTIAL_ID = "af43d884-64a1-4414-897a-680c32374439"

RESPONSES = ResponseSet(
    metadata={"id": CREDENTIAL_ID},
    default=RegisteredResponse(
        service="gcs",
        path=f"/user_credentials/{CREDENTIAL_ID}",
        method="GET",
        json={
            "DATA_TYPE": "result#1.0.0",
            "code": "success",
            "data": [
                {
                    "DATA_TYPE": "user_credential#1.0.0",
                    "connector_id": "145812c8-decc-41f1-83cf-bb2a85a2a70b",
                    "display_name": "posix_credential",
                    "id": CREDENTIAL_ID,
                    "identity_id": "948847d4-ffcc-4ae0-ba3a-a4c88d480159",
                    "invalid": False,
                    "policies": {"DATA_TYPE": "posix_user_credential_policies#1.0.0"},
                    "provisioned": False,
                    "storage_gateway_id": "82247cc9-3208-4d71-bd7f-1b8798c95e6b",
                    "username": "testuser",
                },
            ],
            "detail": "success",
            "has_next_page": False,
            "http_response_code": 200,
        },
    ),
)
