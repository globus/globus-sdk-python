from globus_sdk._testing.models import RegisteredResponse, ResponseSet

CREDENTIAL_ID = "af43d884-64a1-4414-897a-680c32374439"

RESPONSES = ResponseSet(
    metadata={"id": CREDENTIAL_ID},
    default=RegisteredResponse(
        service="gcs",
        path=f"/user_credentials/{CREDENTIAL_ID}",
        method="DELETE",
        json={
            "DATA_TYPE": "result#1.0.0",
            "code": "success",
            "data": [],
            "detail": "success",
            "has_next_page": False,
            "http_response_code": 200,
            "message": f"Deleted User Credential {CREDENTIAL_ID}",
        },
    ),
)
