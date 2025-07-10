import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

_kingfish = {
    "username": "kingfish@globus.org",
    "name": "Christone Ingram",
    "id": str(uuid.uuid1()),
    "email": "kingfish@globus.org",
}
_client_id = str(uuid.uuid1())
_scope = "urn:globus:auth:scope:auth.globus.org:view_identity_set profile email openid"


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token/introspect",
        method="POST",
        json={
            "active": True,
            "token_type": "Bearer",
            "scope": _scope,
            "client_id": _client_id,
            "username": _kingfish["username"],
            "name": _kingfish["name"],
            "email": _kingfish["email"],
            "exp": 1715289767,
            "iat": 1715116967,
            "nbf": 1715116967,
            "sub": _kingfish["id"],
            "aud": [
                "auth.globus.org",
                _client_id,
            ],
            "iss": "https://auth.globus.org",
        },
        metadata={
            "client_id": _client_id,
            "scope": _scope,
            **_kingfish,
        },
    )
)
