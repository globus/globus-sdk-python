from globus_sdk._testing.models import RegisteredResponse, ResponseSet

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        status=200,
        json={
            "access_token": "transfer_access_token",
            "scope": "urn:globus:auth:scope:transfer.api.globus.org:all",
            "expires_in": 172800,
            "token_type": "Bearer",
            "resource_server": "transfer.api.globus.org",
            "state": "_default",
            "other_tokens": [],
        },
    ),
    invalid_grant=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        status=401,
        json={"error": "invalid_grant"},
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
