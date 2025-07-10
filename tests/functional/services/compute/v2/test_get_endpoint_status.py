import globus_sdk
from globus_sdk.testing import load_response


def test_get_endpoint_status(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.get_endpoint_status).metadata
    res = compute_client_v2.get_endpoint_status(endpoint_id=meta["endpoint_id"])
    assert res.http_status == 200
    assert res.data["status"] == "online"
