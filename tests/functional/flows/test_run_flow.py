from typing import Type

from globus_sdk import SpecificFlowClient
from globus_sdk._testing import load_response


def test_run_flow(specific_flow_client_class: Type[SpecificFlowClient]):
    metadata = load_response(SpecificFlowClient.run_flow).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    resp = flow_client.run_flow(**metadata["request_params"])
    assert resp.http_status == 200
