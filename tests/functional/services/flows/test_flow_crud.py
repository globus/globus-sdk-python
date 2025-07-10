import json

import pytest
from responses import matchers

from globus_sdk import MISSING, FlowsAPIError
from globus_sdk.testing import get_last_request, load_response
from globus_sdk.testing.models import RegisteredResponse


@pytest.mark.parametrize("subscription_id", [MISSING, None, "dummy_subscription_id"])
def test_create_flow(flows_client, subscription_id):
    metadata = load_response(flows_client.create_flow).metadata

    resp = flows_client.create_flow(
        **metadata["params"], subscription_id=subscription_id
    )
    assert resp.data["title"] == "Multi Step Transfer"

    last_req = get_last_request()
    req_body = json.loads(last_req.body)
    if subscription_id is not MISSING:
        assert req_body["subscription_id"] == subscription_id
    else:
        assert "subscription_id" not in req_body


@pytest.mark.parametrize("value", [MISSING, [], ["dummy_value"]])
@pytest.mark.parametrize("key", ["run_managers", "run_monitors"])
def test_create_flow_run_role_serialization(flows_client, key, value):

    request_body = {
        "title": "Multi Step Transfer",
        "definition": {
            "StartAt": "Transfer1",
            "States": {
                "Transfer1": {"Type": "Pass", "End": True},
            },
        },
        "input_schema": {},
    }

    if value is not MISSING:
        request_body[key] = value

    load_response(
        RegisteredResponse(
            service="flows",
            path="/flows",
            method="POST",
            json=request_body,
            match=[
                matchers.json_params_matcher(
                    params={
                        "title": request_body["title"],
                        "definition": request_body["definition"],
                        "input_schema": request_body["input_schema"],
                    },
                    strict_match=False,
                )
            ],
        )
    )

    flows_client.create_flow(**request_body)

    last_req = get_last_request()
    req_body = json.loads(last_req.body)

    if value is MISSING:
        assert key not in req_body
    else:
        assert req_body[key] == value


def test_create_flow_error_parsing(flows_client):
    metadata = load_response(
        flows_client.create_flow, case="bad_admin_principal_error"
    ).metadata
    with pytest.raises(FlowsAPIError) as excinfo:
        flows_client.create_flow(**metadata["params"])
    err = excinfo.value
    assert err.code == "UNPROCESSABLE_ENTITY"
    assert err.messages == [
        (
            'Unrecognized principal string: "ae341a98-d274-11e5-b888-dbae3a8ba545". '
            'Allowed principal types in role "FlowAdministrator": '
            "[<AuthGroupUrn>, <AuthIdentityUrn>]"
        ),
        (
            'Unrecognized principal string: "4fab4345-6d20-43a0-9a25-16b2e3bbe765". '
            'Allowed principal types in role "FlowAdministrator": '
            "[<AuthGroupUrn>, <AuthIdentityUrn>]"
        ),
    ]


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


@pytest.mark.parametrize("value", [MISSING, [], ["dummy_value"]])
@pytest.mark.parametrize("key", ["run_managers", "run_monitors"])
def test_update_flow_run_role_serialization(flows_client, key, value):
    metadata = load_response(flows_client.update_flow).metadata
    params = {**metadata["params"], key: value}

    flows_client.update_flow(metadata["flow_id"], **params)

    last_req = get_last_request()
    req_body = json.loads(last_req.body)

    if value is MISSING:
        assert key not in req_body
    else:
        assert req_body[key] == value


def test_delete_flow(flows_client):
    metadata = load_response(flows_client.delete_flow).metadata

    resp = flows_client.delete_flow(metadata["flow_id"])
    assert resp.data["title"] == "Multi Step Transfer"
    assert resp.data["DELETED"] is True
