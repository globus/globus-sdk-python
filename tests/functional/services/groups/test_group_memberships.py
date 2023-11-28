import json
import uuid

import pytest

from globus_sdk import BatchMembershipActions, GroupRole
from globus_sdk._testing import RegisteredResponse, get_last_request, load_response
from tests.common import register_api_route_fixture_file


def test_approve_pending(groups_manager):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556",
        "approve_pending.json",
        method="POST",
    )

    res = groups_manager.approve_pending(
        "d3974728-6458-11e4-b72d-123139141556", "ae332d86-d274-11e5-b885-b31714a110e9"
    )
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert "approve" in data
    assert data["approve"][0]["status"] == "active"


@pytest.mark.parametrize("role", (GroupRole.admin, GroupRole.member, "member", "admin"))
def test_add_member(groups_manager, role):
    rolestr = role if isinstance(role, str) else role.value
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556",
        "add_member.json",
        method="POST",
    )

    res = groups_manager.add_member(
        "d3974728-6458-11e4-b72d-123139141556",
        "ae332d86-d274-11e5-b885-b31714a110e9",
        role=role,
    )
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert "add" in data
    assert data["add"][0]["status"] == "active"
    # FIXME: this should be the line
    #   assert data["add"][0]["role"] == rolestr
    # but the response is fixed right now
    assert data["add"][0]["role"] == "admin"

    req = get_last_request()
    req_body = json.loads(req.body)
    assert req_body["add"][0]["role"] == rolestr


@pytest.mark.parametrize("role", (GroupRole.admin, GroupRole.member, "member", "admin"))
def test_batch_action_payload(groups_client, role):
    group_id = str(uuid.uuid1())
    load_response(
        RegisteredResponse(
            service="groups", method="POST", path=f"/v2/groups/{group_id}", json={}
        )
    )
    rolestr = role if isinstance(role, str) else role.value

    batch_action = (
        BatchMembershipActions()
        .accept_invites(uuid.uuid1())
        .add_members(
            [uuid.uuid1(), uuid.uuid1()],
            role=role,
        )
        .invite_members([uuid.uuid1(), uuid.uuid1()])
        .join([uuid.uuid1(), uuid.uuid1()])
    )

    assert "add" in batch_action
    assert len(batch_action["add"]) == 2
    assert all(member["role"] == role for member in batch_action["add"])

    assert "accept" in batch_action
    assert len(batch_action["accept"]) == 1

    assert "invite" in batch_action
    assert len(batch_action["invite"]) == 2

    assert "join" in batch_action
    assert len(batch_action["invite"]) == 2

    # send the request and confirm that the data is serialized correctly
    groups_client.batch_membership_action(group_id, batch_action)
    req = get_last_request()
    req_body = json.loads(req.body)
    # role should be stringified if it was an enum member
    assert all(member["role"] == rolestr for member in req_body["add"])
    # UUIDs should have been stringified
    for action in ["add", "accept", "invite", "join"]:
        assert all(isinstance(value["identity_id"], str) for value in req_body[action])
