from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import GROUP_ID

RESPONSES = ResponseSet(
    metadata={"group_id": GROUP_ID},
    default=RegisteredResponse(
        service="groups",
        path=f"/groups/{GROUP_ID}/policies",
        method="PUT",
        json={
            "is_high_assurance": False,
            "authentication_assurance_timeout": 28800,
            "group_visibility": "private",
            "group_members_visibility": "managers",
            "join_requests": False,
            "signup_fields": ["address1"],
        },
    ),
)
