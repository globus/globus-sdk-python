import uuid

import globus_sdk
from globus_sdk.testing import load_response

ENDPOINT_CONFIG = """
display_name: My Endpoint
engine:
  type: GlobusComputeEngine
"""


def test_update_endpoint(compute_client_v3: globus_sdk.ComputeClientV3):
    meta = load_response(compute_client_v3.update_endpoint).metadata
    request_doc = {
        "endpoint_name": "my_endpoint",
        "display_name": "My Compute Endpoint",
        "version": "2.31.0",
        "multi_user": False,
        "allowed_functions": [str(uuid.uuid1())],
        "authentication_policy": str(uuid.uuid1()),
        "subscription_uuid": str(uuid.uuid1()),
        "metadata": {
            "endpoint_config": ENDPOINT_CONFIG.strip(),
            "user_config_template": "",
            "user_config_schema": {},
            "description": "My endpoint description",
            "ip_address": "140.221.112.13",
            "hostname": "my-hostname",
            "local_user": "user1",
            "sdk_version": "2.31.0",
            "endpoint_version": "2.31.0",
        },
    }

    res = compute_client_v3.update_endpoint(
        endpoint_id=meta["endpoint_id"], data=request_doc
    )

    assert res.http_status == 200
    assert res.data["endpoint_id"] == meta["endpoint_id"]
