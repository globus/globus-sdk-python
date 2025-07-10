import typing as t

from globus_sdk import SpecificFlowClient
from globus_sdk.testing import load_response


def test_resume_run(specific_flow_client_class: t.Type[SpecificFlowClient]):
    metadata = load_response(SpecificFlowClient.resume_run).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    resp = flow_client.resume_run(metadata["run_id"])
    assert resp.http_status == 200
