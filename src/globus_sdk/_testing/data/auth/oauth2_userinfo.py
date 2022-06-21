from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import ERROR_ID, UNAUTHORIZED_AUTH_RESPONSE_JSON

RESPONSES = ResponseSet(
    metadata={"error_id": ERROR_ID},
    unauthorized=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/userinfo",
        status=401,
        json=UNAUTHORIZED_AUTH_RESPONSE_JSON,
    ),
)
