import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

FOO_CLIENT = {
    "required_idp": None,
    "name": "Great client of FOO",
    "redirect_uris": [],
    "links": {"privacy_policy": None, "terms_and_conditions": None},
    "scopes": [],
    "grant_types": ["authorization_code", "client_credentials", "refresh_token"],
    "id": str(uuid.uuid1()),
    "prompt_for_named_grant": False,
    "fqdns": ["foo.net"],
    "project": "da84e531-1afb-43cb-8c87-135ab580516a",
    "client_type": "client_identity",
    "visibility": "private",
    "parent_client": None,
    "userinfo_from_effective_identity": True,
    "preselect_idp": None,
    "public_client": False,
}

BAR_CLIENT = {
    "required_idp": None,
    "name": "Lessor client of BAR",
    "redirect_uris": [],
    "links": {"privacy_policy": None, "terms_and_conditions": None},
    "scopes": [],
    "grant_types": ["authorization_code", "client_credentials", "refresh_token"],
    "id": str(uuid.uuid1()),
    "prompt_for_named_grant": False,
    "fqdns": ["bar.org"],
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
        path="/v2/api/clients",
        json={"clients": [BAR_CLIENT, FOO_CLIENT]},
        metadata={
            "client_ids": [FOO_CLIENT["id"], BAR_CLIENT["id"]],
        },
    ),
)
