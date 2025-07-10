import typing as t
import uuid

from responses.matchers import json_params_matcher

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

APP_REQUEST_ARGS = {
    "template_id": str(uuid.uuid1()),
    "name": str(uuid.uuid1()).replace("-", ""),
}


def make_app_request_body(request_args: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    request_body = request_args.copy()
    request_body["template_id"] = str(request_args["template_id"])
    return request_body


def make_app_response_body(request_args: t.Mapping[str, t.Any]) -> t.Dict[str, t.Any]:
    return {
        "client": {
            "fqdns": [],
            "name": request_args["name"],
            "id": "e634cc2a-d528-494e-8dda-92ec54a883c9",
            "public_client": False,
            "scopes": [],
            "required_idp": None,
            "grant_types": [
                "authorization_code",
                "client_credentials",
                "refresh_token",
            ],
            "userinfo_from_effective_identity": True,
            "client_type": "confidential_client",
            "prompt_for_named_grant": False,
            "links": {"privacy_policy": None, "terms_and_conditions": None},
            "visibility": "private",
            "preselect_idp": None,
            "parent_client": str(request_args["template_id"]),
            "project": None,
            "redirect_uris": [],
        },
        "included": {
            "client_credential": {
                "name": "Auto-created at client creation",
                "id": "b4840855-2de8-4035-b1b4-4e7c8f518943",
                "client": "e634cc2a-d528-494e-8dda-92ec54a883c9",
                "secret": "cgK1HG9Y0DcZw79YlQEJpZCF4CMxIbaFf5sohWxjcfY=",
            }
        },
    }


def register_response(
    args: t.Mapping[str, t.Any],
) -> RegisteredResponse:
    request_args = {**APP_REQUEST_ARGS, **args}
    request_body = make_app_request_body(request_args)
    response_body = make_app_response_body(request_args)

    return RegisteredResponse(
        service="auth",
        method="POST",
        path="/v2/api/clients",
        json={"client": response_body},
        metadata={
            # Test functions use 'args' to form request
            "args": request_args,
            # Test functions use 'response' to verify response
            "response": response_body,
        },
        match=[
            json_params_matcher(
                {"client": request_body},
            )
        ],
    )


RESPONSES = ResponseSet(
    default=register_response({}),
    template_id_str=register_response({"template_id": str(uuid.uuid1())}),
    template_id_uuid=register_response({"template_id": uuid.uuid1()}),
    name=register_response({"name": str(uuid.uuid1()).replace("-", "")}),
)
