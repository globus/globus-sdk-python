from globus_sdk.testing import load_response


def test_get_group_by_subscription_id(groups_client):
    meta = load_response(groups_client.get_group_by_subscription_id).metadata

    res = groups_client.get_group_by_subscription_id(meta["subscription_id"])
    assert res.http_status == 200
    assert res["group_id"] == meta["group_id"]
    assert "description" not in res
    assert "name" not in res


def test_two_step_get_group_by_subscription_id(groups_client):
    meta = load_response(groups_client.get_group_by_subscription_id).metadata
    load_response(groups_client.get_group, case="subscription").metadata

    res = groups_client.get_group_by_subscription_id(meta["subscription_id"])
    assert res.http_status == 200
    assert res["group_id"] == meta["group_id"]
    assert "description" not in res
    assert "name" not in res

    res2 = groups_client.get_group(meta["group_id"])
    assert res2.http_status == 200
    assert res2["id"] == meta["group_id"]
    assert "name" in res2
