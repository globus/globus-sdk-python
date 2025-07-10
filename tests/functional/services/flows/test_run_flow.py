from __future__ import annotations

import json

import pytest

import globus_sdk
from globus_sdk import FlowsAPIError, SpecificFlowClient
from globus_sdk.testing import get_last_request, load_response


def test_run_flow(specific_flow_client_class: type[SpecificFlowClient]):
    metadata = load_response(SpecificFlowClient.run_flow).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    resp = flow_client.run_flow(**metadata["request_params"])
    assert resp.http_status == 200


def test_run_flow_missing_scope(specific_flow_client_class: type[SpecificFlowClient]):
    metadata = load_response(
        SpecificFlowClient.run_flow, case="missing_scope_error"
    ).metadata

    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    with pytest.raises(FlowsAPIError) as excinfo:
        flow_client.run_flow(**metadata["request_params"])

    err = excinfo.value
    assert err.http_status == 403
    assert err.code == "MISSING_SCOPE"
    assert (
        err.message == "This action requires the following scope: frobulate[demuddle]"
    )


def test_run_flow_without_activity_notification_policy(
    specific_flow_client_class,
):
    metadata = load_response(SpecificFlowClient.run_flow).metadata
    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])
    resp = flow_client.run_flow({})
    assert resp.http_status == 200

    last_req = get_last_request()
    sent_payload = json.loads(last_req.body)
    assert "activity_notification_policy" not in sent_payload


def test_run_flow_with_empty_activity_notification_policy(
    specific_flow_client_class,
):
    metadata = load_response(SpecificFlowClient.run_flow).metadata
    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    policy = globus_sdk.RunActivityNotificationPolicy()
    flow_client.run_flow({}, activity_notification_policy=policy)

    last_req = get_last_request()
    sent_payload = json.loads(last_req.body)
    assert "activity_notification_policy" in sent_payload
    assert sent_payload["activity_notification_policy"] == {}


def test_run_flow_with_activity_notification_policy(
    specific_flow_client_class,
):
    metadata = load_response(SpecificFlowClient.run_flow).metadata
    flow_client = specific_flow_client_class(flow_id=metadata["flow_id"])

    policy = globus_sdk.RunActivityNotificationPolicy(status=["FAILED", "INACTIVE"])
    flow_client.run_flow({}, activity_notification_policy=policy)

    last_req = get_last_request()
    sent_payload = json.loads(last_req.body)
    assert "activity_notification_policy" in sent_payload
    assert sent_payload["activity_notification_policy"] == {
        "status": ["FAILED", "INACTIVE"]
    }
