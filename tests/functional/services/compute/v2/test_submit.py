import uuid

import globus_sdk
from globus_sdk.testing import load_response


def test_submit(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.submit).metadata
    ep_id, func_id = uuid.uuid1(), uuid.uuid1()
    submit_doc = {
        "task_group_id": meta["task_group_id"],
        "create_websocket_queue": False,
        "tasks": [
            [func_id, ep_id, "36\n00\ngASVDAAAAAAAAACMBlJvZG5leZSFlC4=\n12 ..."],
            [func_id, ep_id, "36\n00\ngASVCwAAAAAAAACMBUJvYmJ5lIWULg==\n12 ..."],
        ],
    }

    res = compute_client_v2.submit(data=submit_doc)

    assert res.http_status == 200
    assert res.data["task_group_id"] == meta["task_group_id"]
    results = res.data["results"]
    assert results[0]["task_uuid"] == meta["task_id"]
    assert results[1]["task_uuid"] == meta["task_id_2"]
