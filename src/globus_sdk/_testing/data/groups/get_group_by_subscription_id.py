from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import SUBSCRIPTION_GROUP_ID, SUBSCRIPTION_ID, SUBSCRIPTION_INFO

RESPONSES = ResponseSet(
    metadata={"group_id": SUBSCRIPTION_GROUP_ID, "subscription_id": SUBSCRIPTION_ID},
    default=RegisteredResponse(
        service="groups",
        path=f"/v2/subscription_info/{SUBSCRIPTION_ID}",
        json={
            "group_id": SUBSCRIPTION_GROUP_ID,
            "subscription_id": SUBSCRIPTION_ID,
            # this API returns restricted subscription_info
            "subscription_info": {
                k: v
                for k, v in SUBSCRIPTION_INFO.items()
                if k in ("is_high_assurance", "is_baa", "connectors")
            },
        },
    ),
)
