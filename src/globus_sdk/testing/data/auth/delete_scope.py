import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

SCOPE = {
    "scope_string": "https://auth.globus.org/scopes/3f33d83f-ec0a-4190-887d-0622e7c4ee9a/manager",  # noqa: E501
    "allows_refresh_token": False,
    "id": str(uuid.uuid1()),
    "advertised": False,
    "required_domains": [],
    "name": "Client manage scope",
    "description": "Manage configuration of this client",
    "client": "3f33d83f-ec0a-4190-887d-0622e7c4ee9a",
    "dependent_scopes": [],
}

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        method="DELETE",
        path=f"/v2/api/scopes/{SCOPE['id']}",
        json={"scope": SCOPE},
        metadata={
            "scope_id": SCOPE["id"],
        },
    ),
)
