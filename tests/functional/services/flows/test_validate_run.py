from __future__ import annotations

from globus_sdk import SpecificFlowClient
from globus_sdk._testing import load_response


def test_validate_run(specific_flow_client_class: type[SpecificFlowClient]):
    metadata = load_response(SpecificFlowClient.validate_run).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    resp = flow_client.validate_run(**metadata["request_params"])
    assert resp.http_status == 200


def test_validate_run_returns_error_for_invalid_input(
    specific_flow_client_class: type[SpecificFlowClient],
):
    metadata = load_response(
        SpecificFlowClient.validate_run, case="invalid_body"
    ).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    resp = flow_client.validate_run(**metadata["request_params"])
    assert resp.http_status == 422
