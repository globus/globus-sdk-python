import globus_sdk
from globus_sdk.testing import load_response


def test_get_endpoint_allowlist(compute_client_v3: globus_sdk.ComputeClientV3):
    meta = load_response(compute_client_v3.get_endpoint_allowlist).metadata

    res = compute_client_v3.get_endpoint_allowlist(endpoint_id=meta["endpoint_id"])

    assert res.http_status == 200
    assert res.data["endpoint_id"] == meta["endpoint_id"]
