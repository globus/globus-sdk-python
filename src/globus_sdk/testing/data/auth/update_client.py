import typing as t
import uuid

from responses.matchers import json_params_matcher

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

_COMMON_RESPONSE_RECORD = {
    "fqdns": [],
    "links": {"privacy_policy": None, "terms_and_conditions": None},
    "parent_client": None,
    "preselect_idp": None,
    "prompt_for_named_grant": True,
    "redirect_uris": [],
    "required_idp": None,
    "scopes": [],
    "userinfo_from_effective_identity": True,
}

PUBLIC_CLIENT_RESPONSE_RECORD = {
    "client_type": "public_installed_client",
    "grant_types": ["authorization_code", "refresh_token"],
    **_COMMON_RESPONSE_RECORD,
}


def register_response(
    args: t.Mapping[str, t.Any],
) -> RegisteredResponse:
    # Some name of args to create_client() have differenlty named fields.
    body_fields: t.Dict[str, t.Any] = {}
    for arg_name in args:
        if arg_name == "terms_and_conditions" or arg_name == "privacy_policy":
            body_fields["links"] = {
                arg_name: args[arg_name],
                **body_fields.get("links", {}),
            }
        else:
            body_fields[arg_name] = args[arg_name]

    client_id = str(uuid.uuid1())

    # Default to a public client response unless arg says otherwise
    client_response_record = {
        **PUBLIC_CLIENT_RESPONSE_RECORD,
        **body_fields,
        "id": client_id,
    }

    return RegisteredResponse(
        service="auth",
        method="PUT",
        path=f"/v2/api/clients/{client_id}",
        json={"client": client_response_record},
        metadata={
            # Test functions use 'args' to form request
            "args": {**args, "client_id": client_id},
            # Test functions use 'response' to verify response
            "response": body_fields,
        },
        match=[json_params_matcher({"client": body_fields})],
    )


RESPONSES = ResponseSet(
    default=register_response({}),
    name=register_response({"name": str(uuid.uuid4()).replace("-", "")}),
    publicly_visible=register_response({"visibility": "public"}),
    not_publicly_visible=register_response({"visibility": "private"}),
    redirect_uris=register_response({"redirect_uris": ["https://foo.com"]}),
    links=register_response(
        {
            "terms_and_conditions": "https://foo.org",
            "privacy_policy": "https://boo.org",
        }
    ),
    required_idp=register_response({"required_idp": str(uuid.uuid1())}),
    preselect_idp=register_response({"preselect_idp": str(uuid.uuid1())}),
)
