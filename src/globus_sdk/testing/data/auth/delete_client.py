import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

CLIENT = {
    "required_idp": None,
    "name": "Great client of FOO",
    "redirect_uris": [],
    "links": {"privacy_policy": None, "terms_and_conditions": None},
    "scopes": [],
    "grant_types": ["authorization_code", "client_credentials", "refresh_token"],
    "id": str(uuid.uuid1()),
    "prompt_for_named_grant": False,
    "fqdns": ["globus.org"],
    "project": "da84e531-1afb-43cb-8c87-135ab580516a",
    "client_type": "client_identity",
    "visibility": "private",
    "parent_client": None,
    "userinfo_from_effective_identity": True,
    "preselect_idp": None,
    "public_client": False,
}

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        method="DELETE",
        path=f"/v2/api/clients/{CLIENT['id']}",
        json={"client": CLIENT},
        metadata={
            "client_id": CLIENT["id"],
        },
    ),
)
