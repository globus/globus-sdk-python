import pytest

from globus_sdk import FlowCreateRequest, FlowsClient
from globus_sdk._testing import load_response

_SIMPLE_DEF = {
    "StartAt": "my-state",
    "States": {"my-state": {"Type": "Pass", "End": True}},
}
_REQUIRED_PARAMS = {"title": "my-flow", "definition": _SIMPLE_DEF, "input_schema": {}}


def test_create_flow(flows_client: FlowsClient):
    metadata = load_response(flows_client.create_flow).metadata

    resp = flows_client.create_flow(data=metadata["params"])
    assert resp.data["title"] == "Multi Step Transfer"


def test_create_flow_with_payload_wrapper(flows_client: FlowsClient):
    metadata = load_response(flows_client.create_flow).metadata
    create_request = FlowCreateRequest(**metadata["params"])

    resp = flows_client.create_flow(create_request)
    assert resp.data["title"] == "Multi Step Transfer"


def test_flow_create_request_invalidates_bad_title():
    with pytest.raises(ValueError):
        FlowCreateRequest(**{**_REQUIRED_PARAMS, "title": "a" * 129})

    with pytest.raises(ValueError):
        FlowCreateRequest(**{**_REQUIRED_PARAMS, "title": "" * 129})


def test_flow_create_request_invalidates_bad_subtitle():
    with pytest.raises(ValueError):
        FlowCreateRequest(**_REQUIRED_PARAMS, subtitle="a" * 129)


def test_flow_create_request_invalidates_bad_description():
    with pytest.raises(ValueError):
        FlowCreateRequest(**_REQUIRED_PARAMS, description="a" * 4097)


def test_flow_create_request_invalidates_bad_flow_viewers():
    with pytest.raises(ValueError):
        FlowCreateRequest(**_REQUIRED_PARAMS, flow_viewers=["not-a-real-flow-viewer"])

    with pytest.raises(ValueError):
        FlowCreateRequest(
            **_REQUIRED_PARAMS,
            flow_viewers=[
                "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150"
                "not-a-real-flow-viewer"
            ]
        )

    with pytest.raises(ValueError):
        FlowCreateRequest(**_REQUIRED_PARAMS, flow_viewers=["all_authenticated_users"])


def test_flow_create_request_invalidates_bad_flow_starters():
    with pytest.raises(ValueError):
        FlowCreateRequest(**_REQUIRED_PARAMS, flow_starters=["not-a-real-flow-starter"])

    with pytest.raises(ValueError):
        FlowCreateRequest(
            **_REQUIRED_PARAMS,
            flow_starters=[
                "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150"
                "not-a-real-flow-starter"
            ]
        )

    with pytest.raises(ValueError):
        FlowCreateRequest(**_REQUIRED_PARAMS, flow_starters=["public"])


def test_flow_create_request_invalidates_bad_flow_administrators():
    with pytest.raises(ValueError):
        FlowCreateRequest(
            **_REQUIRED_PARAMS, flow_administrators=["not-a-real-flow-administrator"]
        )

    with pytest.raises(ValueError):
        FlowCreateRequest(
            **_REQUIRED_PARAMS,
            flow_administrators=[
                "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150"
                "not-a-real-flow-administrator"
            ]
        )


def test_flow_create_request_invalidates_bad_keywords():
    with pytest.raises(ValueError):
        FlowCreateRequest(**_REQUIRED_PARAMS, keywords=["a" for _ in range(1025)])


def test_flow_create_request_invalidates_bad_subscription_id():
    with pytest.raises(ValueError):
        FlowCreateRequest(**_REQUIRED_PARAMS, subscription_id="definitely-not-a-uuid")
