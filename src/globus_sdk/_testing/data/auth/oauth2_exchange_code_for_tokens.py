from globus_sdk._testing.models import RegisteredResponse, ResponseSet

RESPONSES = ResponseSet(
    invalid_grant=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        status=401,
        json={"error": "invalid_grant"},
    )
)
