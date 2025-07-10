from globus_sdk.testing import load_response


def test_delete_group(groups_client):
    meta = load_response(groups_client.delete_group).metadata

    res = groups_client.delete_group(group_id=meta["group_id"])
    assert res.http_status == 200
    assert "Claptrap" in res["name"]
