from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import FORBIDDEN_AUTH_RESPONSE, UNAUTHORIZED_AUTH_RESPONSE

RESPONSES = ResponseSet(
    unauthorized=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/userinfo",
        status=401,
        json=UNAUTHORIZED_AUTH_RESPONSE.json,
        metadata={
            "error_id": UNAUTHORIZED_AUTH_RESPONSE.error_id,
            **UNAUTHORIZED_AUTH_RESPONSE.metadata_include,
        },
    ),
    forbidden=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/userinfo",
        status=403,
        json=FORBIDDEN_AUTH_RESPONSE.json,
        metadata={
            "error_id": FORBIDDEN_AUTH_RESPONSE.error_id,
            **FORBIDDEN_AUTH_RESPONSE.metadata_include,
        },
    ),
)
