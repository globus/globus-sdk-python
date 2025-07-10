import globus_sdk
from globus_sdk.testing import load_response


def test_get_task(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.get_task).metadata
    res = compute_client_v2.get_task(task_id=meta["task_id"])
    assert res.http_status == 200
    assert res.data["task_id"] == meta["task_id"]
