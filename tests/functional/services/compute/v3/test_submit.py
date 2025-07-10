import globus_sdk
from globus_sdk.testing import load_response


def test_submit(compute_client_v3: globus_sdk.ComputeClientV3):
    meta = load_response(compute_client_v3.submit).metadata
    submit_doc = {
        "tasks": {
            meta["function_id"]: [
                "36\n00\ngASVDAAAAAAAAACMBlJvZG5leZSFlC4=\n12 ...",
                "36\n00\ngASVCwAAAAAAAACMBUJvYmJ5lIWULg==\n12 ...",
            ],
        },
        "task_group_id": meta["task_group_id"],
        "create_queue": True,
        "user_runtime": {
            "globus_compute_sdk_version": "2.29.0",
            "globus_sdk_version": "3.46.0",
            "python_version": "3.11.9",
        },
    }

    res = compute_client_v3.submit(endpoint_id=meta["endpoint_id"], data=submit_doc)

    assert res.http_status == 200
    assert res.data["request_id"] == meta["request_id"]
    assert res.data["task_group_id"] == meta["task_group_id"]
    assert res.data["endpoint_id"] == meta["endpoint_id"]
    assert res.data["tasks"] == {
        meta["function_id"]: [meta["task_id"], meta["task_id_2"]]
    }
