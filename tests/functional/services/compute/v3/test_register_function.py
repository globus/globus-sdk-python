import globus_sdk
from globus_sdk.testing import load_response


def test_register_function(compute_client_v3: globus_sdk.ComputeClientV3):
    meta = load_response(compute_client_v3.register_function).metadata
    registration_doc = {
        "function_name": meta["function_name"],
        "function_code": meta["function_code"],
    }
    res = compute_client_v3.register_function(data=registration_doc)
    assert res.http_status == 200
    assert res.data["function_uuid"] == meta["function_id"]
