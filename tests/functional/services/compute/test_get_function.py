import globus_sdk
from globus_sdk._testing import load_response


def test_get_function(compute_client: globus_sdk.ComputeClient):
    meta = load_response(compute_client.get_function).metadata
    res = compute_client.get_function(function_id=meta["function_id"])
    assert res.http_status == 200
    assert res.data["function_uuid"] == meta["function_id"]
    assert res.data["function_name"] == meta["function_name"]
    assert res.data["function_code"] == meta["function_code"]
