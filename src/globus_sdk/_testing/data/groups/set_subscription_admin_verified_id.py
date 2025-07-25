from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import GROUP_ID, SUBSCRIPTION_ID

RESPONSES = ResponseSet(
    metadata={"group_id": GROUP_ID, "subscription_id": SUBSCRIPTION_ID},
    default=RegisteredResponse(
        service="groups",
        path=f"/groups/{GROUP_ID}/subscription_admin_verified",
        method="PUT",
        json={
            "group_id": GROUP_ID,
            "subscription_admin_verified_id": SUBSCRIPTION_ID,
        },
    ),
)
