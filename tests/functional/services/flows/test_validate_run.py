from __future__ import annotations

import pytest

from globus_sdk import FlowsAPIError, SpecificFlowClient
from globus_sdk.testing import load_response


def test_validate_run(specific_flow_client_class: type[SpecificFlowClient]):
    metadata = load_response(SpecificFlowClient.validate_run).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    resp = flow_client.validate_run(body=metadata["request_body"])
    assert resp.http_status == 200


def test_validate_run_returns_error_for_invalid_payload(
    specific_flow_client_class: type[SpecificFlowClient],
):
    metadata = load_response(
        SpecificFlowClient.validate_run, case="invalid_input_payload"
    ).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    with pytest.raises(FlowsAPIError) as error:
        flow_client.validate_run(body=metadata["request_body"])
    assert error.value.http_status == 400


def test_validate_run_returns_error_for_lacking_run_permission(
    specific_flow_client_class: type[SpecificFlowClient],
):
    metadata = load_response(
        SpecificFlowClient.validate_run, case="not_a_flow_starter"
    ).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    with pytest.raises(FlowsAPIError) as error:
        flow_client.validate_run(body=metadata["request_body"])
    assert error.value.http_status == 403
