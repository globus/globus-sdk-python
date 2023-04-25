import typing as t

from globus_sdk import SpecificFlowClient
from globus_sdk._testing import load_response


def test_run_flow(specific_flow_client_class: t.Type[SpecificFlowClient]):
    metadata = load_response(SpecificFlowClient.run_flow).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    resp = flow_client.run_flow(**metadata["request_params"])
    assert resp.http_status == 200


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
