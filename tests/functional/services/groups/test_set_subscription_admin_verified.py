from globus_sdk.testing import get_last_request, load_response
from tests.common import fast_json


def test_set_subscription_admin_verified(groups_client):
    meta = load_response(groups_client.set_subscription_admin_verified).metadata

    res = groups_client.set_subscription_admin_verified(
        group_id=meta["group_id"],
        subscription_id=meta["subscription_id"],
    )
    assert res.http_status == 200
    assert res.data["group_id"] == meta["group_id"]
    assert res.data["subscription_admin_verified_id"] == meta["subscription_id"]

    req = get_last_request()
    req = fast_json.loads(req.body)
    assert req == {"subscription_admin_verified_id": meta["subscription_id"]}
