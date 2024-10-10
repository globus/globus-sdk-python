import globus_sdk
from globus_sdk._testing import load_response


def test_delete_function(compute_client: globus_sdk.ComputeClient):
    meta = load_response(compute_client.delete_function).metadata
    res = compute_client.delete_function(function_id=meta["function_id"])
    assert res.http_status == 200
    assert res.data == {"result": 302}
