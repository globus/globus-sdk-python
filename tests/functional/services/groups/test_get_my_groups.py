from globus_sdk._testing import load_response
from globus_sdk.response import ArrayResponse


def test_get_my_groups(groups_client):
    meta = load_response(groups_client.get_my_groups).metadata

    res = groups_client.get_my_groups()
    assert res.http_status == 200

    assert isinstance(res, ArrayResponse)
    assert isinstance(res.data, list)
    assert set(meta["group_names"]) == {g["name"] for g in res}
