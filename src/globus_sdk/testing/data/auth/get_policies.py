import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

GREEN_LIGHT_POLICY = {
    "high_assurance": False,
    "domain_constraints_include": ["greenlight.org"],
    "display_name": "GreenLight domain Only Policy",
    "description": "Only allow access from @greenlight.org",
    "id": str(uuid.uuid1()),
    "domain_constraints_exclude": None,
    "project_id": "da84e531-1afb-43cb-8c87-135ab580516a",
    "authentication_assurance_timeout": 35,
    "required_mfa": False,
}

RED_LIGHT_POLICY = {
    "high_assurance": True,
    "domain_constraints_include": None,
    "display_name": "No RedLight domain Policy",
    "description": "Disallow access from @redlight.org",
    "id": str(uuid.uuid1()),
    "domain_constraints_exclude": ["redlight.org"],
    "project_id": "da84e531-1afb-43cb-8c87-135ab580516a",
    "authentication_assurance_timeout": 35,
    "required_mfa": False,
}

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path="/v2/api/policies",
        json={"policies": [GREEN_LIGHT_POLICY, RED_LIGHT_POLICY]},
        metadata={
            "policy_ids": [GREEN_LIGHT_POLICY["id"], RED_LIGHT_POLICY["id"]],
        },
    )
)
