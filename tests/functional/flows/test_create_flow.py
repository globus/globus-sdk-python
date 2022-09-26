from globus_sdk import FlowsClient
from globus_sdk._testing import load_response


def test_create_flow(flows_client: FlowsClient):
    metadata = load_response(flows_client.create_flow).metadata

    resp = flows_client.create_flow(**metadata["params"])
    assert resp.data["title"] == "Multi Step Transfer"
