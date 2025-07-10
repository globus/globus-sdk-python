import globus_sdk
from globus_sdk.testing import load_response


def test_lock_endpoint(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.lock_endpoint).metadata

    res = compute_client_v2.lock_endpoint(endpoint_id=meta["endpoint_id"])

    assert res.http_status == 200
    assert res.data["endpoint_id"] == meta["endpoint_id"]
