import typing as t
import uuid

from responses.matchers import json_params_matcher

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

POLICY_REQUEST_ARGS = {
    "policy_id": str(uuid.uuid1()),
}


def make_request_body(request_args: t.Mapping[str, t.Any]) -> t.Dict[str, t.Any]:
    request_body = {}

    for field in [
        "authentication_assurance_timeout",
        "required_mfa",
        "display_name",
        "description",
        "domain_constraints_include",
        "domain_constraints_exclude",
    ]:
        if field in request_args:
            request_body[field] = request_args[field]

    if "project_id" in request_args:
        request_body["project_id"] = str(request_args["project_id"])

    return request_body


def make_response_body(request_args: t.Mapping[str, t.Any]) -> t.Dict[str, t.Any]:
    return {
        "project_id": str(request_args.get("project_id", uuid.uuid1())),
        "high_assurance": request_args.get("high_assurance", True),
        "required_mfa": request_args.get("required_mfa", False),
        "authentication_assurance_timeout": request_args.get(
            "authentication_assurance_timeout", 25
        ),
        "display_name": request_args.get(
            "display_name", str(uuid.uuid4()).replace("-", "")
        ),
        "description": request_args.get(
            "description", str(uuid.uuid4()).replace("-", "")
        ),
        "domain_constraints_include": request_args.get("domain_constraints_include"),
        "domain_constraints_exclude": request_args.get("domain_constraints_exclude"),
    }


def register_response(
    args: t.Mapping[str, t.Any],
) -> RegisteredResponse:
    request_args = {**POLICY_REQUEST_ARGS, **args}
    request_body = make_request_body(request_args)
    response_body = make_response_body(request_args)

    return RegisteredResponse(
        service="auth",
        method="PUT",
        path=f"/v2/api/policies/{request_args['policy_id']}",
        json={"policy": response_body},
        metadata={
            # Test functions use 'args' to form request
            "args": request_args,
            # Test functions use 'response' to verify response
            "response": response_body,
        },
        match=[json_params_matcher({"policy": request_body})],
    )


RESPONSES = ResponseSet(
    default=register_response({}),
    project_id_str=register_response({"project_id": str(uuid.uuid1())}),
    project_id_uuid=register_response({"project_id": uuid.uuid1()}),
    authentication_assurance_timeout=register_response(
        {"authentication_assurance_timeout": 9100}
    ),
    required_mfa=register_response({"required_mfa": True}),
    not_required_mfa=register_response({"required_mfa": False}),
    display_name=register_response(
        {"display_name": str(uuid.uuid4()).replace("-", "")}
    ),
    description=register_response({"description": str(uuid.uuid4()).replace("-", "")}),
    no_domain_constrants_include=register_response(
        {"domain_constraints_include": None}
    ),
    empty_domain_constrants_include=register_response(
        {"domain_constraints_include": []}
    ),
    domain_constrants_include=register_response(
        {"domain_constraints_include": ["globus.org", "uchicago.edu"]}
    ),
    no_domain_constrants_exclude=register_response(
        {"domain_constraints_exclude": None}
    ),
    empty_domain_constrants_exclude=register_response(
        {"domain_constraints_exclude": []}
    ),
    domain_constrants_exclude=register_response(
        {"domain_constraints_exclude": ["globus.org", "uchicago.edu"]}
    ),
)
