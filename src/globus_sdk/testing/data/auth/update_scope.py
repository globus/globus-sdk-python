import typing as t
import uuid

from responses.matchers import json_params_matcher

from globus_sdk import DependentScopeSpec
from globus_sdk._testing.models import RegisteredResponse, ResponseSet

SCOPE_REQUEST_ARGS = {
    "scope_id": str(uuid.uuid1()),
}


def make_request_body(request_args: t.Mapping[str, t.Any]) -> t.Dict[str, t.Any]:
    request_body = {}

    for field in [
        "name",
        "description",
        "scope_suffix",
        "advertised",
        "allows_refresh_token",
        "required_domains",
    ]:
        if field in request_args and request_args[field] is not None:
            request_body[field] = request_args[field]

    if "dependent_scopes" in request_args:
        request_body["dependent_scopes"] = request_args["dependent_scopes"]

    return request_body


def make_response_body(request_args: t.Mapping[str, t.Any]) -> t.Dict[str, t.Any]:
    client_id = str(uuid.uuid1())
    scope_suffix = request_args.get("scope_suffix", str(uuid.uuid4()).replace("-", ""))

    return {
        "scope_string": f"https://auth.globus.org/scopes/{client_id}/{scope_suffix}",
        "allows_refresh_token": request_args.get("allows_refresh_token", True),
        "id": request_args["scope_id"],
        "advertised": request_args.get("advertised", False),
        "required_domains": request_args.get("required_domains", []),
        "name": request_args.get("name", str(uuid.uuid4()).replace("-", "")),
        "description": request_args.get(
            "description", str(uuid.uuid4()).replace("-", "")
        ),
        "client": str(request_args.get("client_id", uuid.uuid1())),
        "dependent_scopes": [
            {
                "scope": str(ds["scope"]),
                "optional": ds["optional"],
                "requires_refresh_token": ds["requires_refresh_token"],
            }
            for ds in request_args.get("dependent_scopes", [])
        ],
    }


def register_response(
    args: t.Mapping[str, t.Any],
) -> RegisteredResponse:
    request_args = {**SCOPE_REQUEST_ARGS, **args}
    request_body = make_request_body(request_args)
    response_body = make_response_body(request_args)

    return RegisteredResponse(
        service="auth",
        method="PUT",
        path=f"/v2/api/scopes/{request_args['scope_id']}",
        json={"scope": response_body},
        metadata={
            # Test functions use 'args' to form request
            "args": request_args,
            # Test functions use 'response' to verify response
            "response": response_body,
        },
        match=[json_params_matcher({"scope": request_body})],
    )


RESPONSES = ResponseSet(
    default=register_response({}),
    name=register_response({"name": str(uuid.uuid4()).replace("-", "")}),
    description=register_response({"description": str(uuid.uuid4()).replace("-", "")}),
    scope_suffix=register_response(
        {"scope_suffix": str(uuid.uuid4()).replace("-", "")}
    ),
    no_required_domains=register_response({"required_domains": []}),
    required_domains=register_response(
        {"required_domains": ["globus.org", "uchicago.edu"]}
    ),
    no_dependent_scopes=register_response({"dependent_scopes": []}),
    dependent_scopes=register_response(
        {
            "dependent_scopes": [
                DependentScopeSpec(str(uuid.uuid1()), True, True),
                DependentScopeSpec(uuid.uuid1(), False, False),
            ],
        }
    ),
    advertised=register_response({"advertised": True}),
    not_advertised=register_response({"advertised": False}),
    allows_refresh_token=register_response({"allows_refresh_token": True}),
    disallows_refresh_token=register_response({"allows_refresh_token": False}),
)
