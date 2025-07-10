from globus_sdk.testing.models import RegisteredResponse, ResponseSet

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token/revoke",
        method="POST",
        json={"active": False},
    )
)
