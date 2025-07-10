import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

POLICY = {
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

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        method="DELETE",
        path=f"/v2/api/policies/{POLICY['id']}",
        json={"policy": POLICY},
        metadata={
            "policy_id": POLICY["id"],
        },
    )
)
