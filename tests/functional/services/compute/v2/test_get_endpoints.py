import urllib.parse

import globus_sdk
from globus_sdk._testing import get_last_request, load_response


def test_get_endpoints(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.get_endpoints).metadata

    res = compute_client_v2.get_endpoints()

    assert res.http_status == 200
    assert res.data[0]["uuid"] == meta["endpoint_id"]
    assert res.data[1]["uuid"] == meta["endpoint_id_2"]

    # confirm that the 'role' param was not sent
    last_req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(last_req.url).query)
    assert "role" not in parsed_qs


def test_get_endpoints_any(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.get_endpoints, case="any").metadata
    res = compute_client_v2.get_endpoints(role="any")

    last_req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(last_req.url).query)
    assert parsed_qs["role"] == ["any"]

    assert res.http_status == 200
    assert res.data[0]["uuid"] == meta["endpoint_id"]
    assert res.data[1]["uuid"] == meta["endpoint_id_2"]
    assert res.data[2]["uuid"] == meta["endpoint_id_3"]
    assert res.data[1]["owner"] != res.data[2]["owner"]
