import globus_sdk
from globus_sdk.testing import load_response


def test_get_task_group(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.get_task_group).metadata
    res = compute_client_v2.get_task_group(task_group_id=meta["task_group_id"])
    assert res.http_status == 200
    assert meta["task_group_id"] == res.data["taskgroup_id"]
    assert meta["task_id"] == res.data["tasks"][0]["id"]
    assert meta["task_id_2"] == res.data["tasks"][1]["id"]
