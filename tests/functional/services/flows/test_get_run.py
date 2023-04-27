from globus_sdk._testing import load_response


def test_get_run(flows_client):
    metadata = load_response(flows_client.get_run).metadata

    resp = flows_client.get_run(metadata["run_id"])
    assert resp.http_status == 200
    assert "flow_description" not in resp


def test_get_run_with_flow_description(flows_client):
    metadata = load_response(flows_client.get_run).metadata

    resp = flows_client.get_run(metadata["run_id"], include_flow_description=True)
    assert resp.http_status == 200
    assert "flow_description" in resp
