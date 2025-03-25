import typing as t
import uuid

from responses.matchers import json_params_matcher

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

POLICY_REQUEST_ARGS = {
    "project_id": str(uuid.uuid1()),
    "display_name": "Policy of Foo",
    "description": "Controls access to Foo",
}


def make_request_body(request_args: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    request_body = request_args.copy()
    request_body["project_id"] = str(request_args["project_id"])

    for domain_constraints in [
        "domain_constraints_include",
        "domain_constraints_exclude",
    ]:
        if domain_constraints in request_args:
            request_body[domain_constraints] = request_args[domain_constraints]

    return request_body


def make_response_body(request_args: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    response_body = request_args.copy()
    response_body["project_id"] = str(request_args["project_id"])
    response_body["id"] = str(uuid.uuid1())

    for domain_constraints in [
        "domain_constraints_include",
        "domain_constraints_exclude",
    ]:
        if domain_constraints in request_args:
            response_body[domain_constraints] = request_args.get(domain_constraints)

    return response_body


def register_response(
    args: t.Mapping[str, t.Any],
    match: t.Any = None,
) -> RegisteredResponse:
    request_args = {**POLICY_REQUEST_ARGS, **args}
    request_body = make_request_body(request_args)
    response_body = make_response_body(request_args)

    return RegisteredResponse(
        service="auth",
        method="POST",
        path="/v2/api/policies",
        json={"policy": response_body},
        metadata={
            # Test functions use 'args' to form request
            "args": request_args,
            # Test functions use 'response' to verify response
            "response": response_body,
        },
        match=(
            [json_params_matcher({"policy": request_body})] if match is None else match
        ),
    )


RESPONSES = ResponseSet(
    default=register_response({}, match=[]),
    project_id_str=register_response({"project_id": str(uuid.uuid1())}),
    project_id_uuid=register_response({"project_id": uuid.uuid1()}),
    high_assurance=register_response(
        {
            "high_assurance": True,
            "authentication_assurance_timeout": 35,
            "required_mfa": False,
        }
    ),
    not_high_assurance=register_response(
        {"high_assurance": False, "required_mfa": False}
    ),
    required_mfa=register_response(
        {
            "high_assurance": True,
            "authentication_assurance_timeout": 45,
            "required_mfa": True,
        }
    ),
    authentication_assurance_timeout=register_response(
        {"authentication_assurance_timeout": 23}
    ),
    display_name=register_response(
        {"display_name": str(uuid.uuid4()).replace("-", "")}
    ),
    description=register_response({"description": str(uuid.uuid4()).replace("-", "")}),
    domain_constraints_include=register_response(
        {
            "domain_constraints_include": ["globus.org", "uchicago.edu"],
        },
    ),
    empty_domain_constraints_include=register_response(
        {
            "domain_constraints_include": [],
        },
    ),
    no_domain_constraints_include=register_response(
        {
            "domain_constraints_include": None,
        },
    ),
    domain_constraints_exclude=register_response(
        {
            "domain_constraints_exclude": ["globus.org", "uchicago.edu"],
        },
    ),
    empty_domain_constraints_exclude=register_response(
        {
            "domain_constraints_exclude": [],
        },
    ),
    no_domain_constraints_exclude=register_response(
        {
            "domain_constraints_exclude": None,
        },
    ),
)
