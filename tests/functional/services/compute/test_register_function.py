import globus_sdk
from globus_sdk._testing import load_response
from globus_sdk.services.compute import ComputeFunctionDocument


def test_register_function(compute_client: globus_sdk.ComputeClient):
    meta = load_response(compute_client.register_function).metadata
    function_doc = ComputeFunctionDocument(
        function_name=meta["function_name"], function_code=meta["function_code"]
    )
    res = compute_client.register_function(function_doc)
    assert res.http_status == 200
    assert res.data["function_uuid"] == meta["function_id"]
