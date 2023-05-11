from globus_sdk._testing import load_response


def test_create_flow(flows_client):
    metadata = load_response(flows_client.create_flow).metadata

    resp = flows_client.create_flow(**metadata["params"])
    assert resp.data["title"] == "Multi Step Transfer"


def test_get_flow(flows_client):
    meta = load_response(flows_client.get_flow).metadata
    resp = flows_client.get_flow(meta["flow_id"])
    assert resp.data["title"] == meta["title"]


def test_update_flow(flows_client):
    meta = load_response(flows_client.update_flow).metadata
    resp = flows_client.update_flow(meta["flow_id"], **meta["params"])
    for k, v in meta["params"].items():
        assert k in resp
        assert resp[k] == v


def test_delete_flow(flows_client):
    metadata = load_response(flows_client.delete_flow).metadata

    resp = flows_client.delete_flow(metadata["flow_id"])
    assert resp.data["title"] == "Multi Step Transfer"
    assert resp.data["DELETED"] is True
