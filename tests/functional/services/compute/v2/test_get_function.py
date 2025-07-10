import globus_sdk
from globus_sdk.testing import load_response


def test_get_function(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.get_function).metadata
    res = compute_client_v2.get_function(function_id=meta["function_id"])
    assert res.http_status == 200
    assert res.data["function_uuid"] == meta["function_id"]
    assert res.data["function_name"] == meta["function_name"]
    assert res.data["function_code"] == meta["function_code"]
