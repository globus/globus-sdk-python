from globus_sdk._testing import load_response


def test_list_flows_simple(flows_client):
    meta = load_response(flows_client.list_flows).metadata

    res = flows_client.list_flows()
    assert res.http_status == 200
    assert meta["first_flow_id"] == res["flows"][0]["id"]
