from globus_sdk._testing.models import RegisteredResponse, ResponseSet

_token = "DUMMY_TRANSFER_TOKEN_FROM_THE_INTERTUBES"
_scope = "urn:globus:auth:scope:transfer.api.globus.org:all"

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        status=200,
        json={
            "access_token": _token,
            "scope": _scope,
            "expires_in": 172800,
            "token_type": "Bearer",
            "resource_server": "transfer.api.globus.org",
            "other_tokens": [],
        },
        metadata={
            "service": "transfer",
            "resource_server": "transfer.api.globus.org",
            "access_token": _token,
            "scope": _scope,
        },
    ),
    openid=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        status=200,
        json={
            "access_token": "auth_access_token",
            "scope": "openid",
            "expires_in": 172800,
            "token_type": "Bearer",
            "resource_server": "auth.globus.org",
            "id_token": "openid_token",
            "other_tokens": [],
        },
    ),
)
