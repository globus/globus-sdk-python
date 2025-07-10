from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import (
    BASE_GROUP_DOC,
    GROUP_ID,
    SUBSCRIPTION_GROUP_DOC,
    SUBSCRIPTION_GROUP_ID,
    SUBSCRIPTION_ID,
)

RESPONSES = ResponseSet(
    metadata={"group_id": GROUP_ID},
    default=RegisteredResponse(
        service="groups",
        path=f"/v2/groups/{GROUP_ID}",
        json=BASE_GROUP_DOC,
    ),
    subscription=RegisteredResponse(
        service="groups",
        path=f"/v2/groups/{SUBSCRIPTION_GROUP_ID}",
        json=SUBSCRIPTION_GROUP_DOC,
        metadata={
            "group_id": SUBSCRIPTION_GROUP_ID,
            "subscription_id": SUBSCRIPTION_ID,
        },
    ),
)
