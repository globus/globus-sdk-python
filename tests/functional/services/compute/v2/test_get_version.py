import globus_sdk
from globus_sdk.testing import load_response


def test_get_version(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.get_version).metadata
    res = compute_client_v2.get_version()
    assert res.http_status == 200
    assert res.data == meta["api_version"]


def test_get_version_all(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.get_version, case="all").metadata
    res = compute_client_v2.get_version(service="all")
    assert res.http_status == 200
    assert res.data["api"] == meta["api_version"]
