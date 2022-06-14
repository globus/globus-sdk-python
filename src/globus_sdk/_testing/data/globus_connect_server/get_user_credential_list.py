from globus_sdk._testing.models import RegisteredResponse, ResponseSet

CREDENTIAL_IDS = [
    "af43d884-64a1-4414-897a-680c32374439",
    "c96b8f70-1448-46db-89af-292623c93ee4",
]

RESPONSES = ResponseSet(
    metadata={"ids": CREDENTIAL_IDS},
    default=RegisteredResponse(
        service="gcs",
        path="/user_credentials",
        method="GET",
        json={
            "DATA_TYPE": "result#1.0.0",
            "code": "success",
            "data": [
                {
                    "DATA_TYPE": "user_credential#1.0.0",
                    "connector_id": "145812c8-decc-41f1-83cf-bb2a85a2a70b",
                    "display_name": "posix_credential",
                    "id": CREDENTIAL_IDS[0],
                    "identity_id": "948847d4-ffcc-4ae0-ba3a-a4c88d480159",
                    "invalid": False,
                    "policies": {"DATA_TYPE": "posix_user_credential_policies#1.0.0"},
                    "provisioned": False,
                    "storage_gateway_id": "82247cc9-3208-4d71-bd7f-1b8798c95e6b",
                    "username": "testuser",
                },
                {
                    "DATA_TYPE": "user_credential#1.0.0",
                    "connector_id": "7643e831-5f6c-4b47-a07f-8ee90f401d23",
                    "display_name": "s3_credential",
                    "id": CREDENTIAL_IDS[1],
                    "identity_id": "948847d4-ffcc-4ae0-ba3a-a4c88d480159",
                    "invalid": False,
                    "policies": {
                        "DATA_TYPE": "s3_user_credential_policies#1.0.0",
                        "s3_key_id": "key_id",
                        "s3_secret_key": "key_secret",
                    },
                    "provisioned": True,
                    "storage_gateway_id": "99aab7ac-8fde-40e2-b6db-44de8e59597a",
                    "username": "testuser",
                },
            ],
            "detail": "success",
            "has_next_page": False,
            "http_response_code": 200,
        },
        metadata={"ids": CREDENTIAL_IDS},
    ),
)
