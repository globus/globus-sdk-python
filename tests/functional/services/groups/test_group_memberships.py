import json

import pytest

from globus_sdk import BatchMembershipActions, GroupRole
from globus_sdk._testing import get_last_request
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
def test_batch_action_payload(role):
    rolestr = role if isinstance(role, str) else role.value

    batch_action = (
        BatchMembershipActions()
        .accept_invites("ae332d86-d274-11e5-b885-b31714a110e9")
        .add_members(
            [
                "788e8a5e-da7f-11eb-9782-97fc8494b14e",
                "79c411f0-da7f-11eb-a0e4-a3451dad6f05",
            ],
            role=role,
        )
        .invite_members(
            [
                "888e8a5e-da7f-11eb-9782-97fc8494b14e",
                "89c411f0-da7f-11eb-a0e4-a3451dad6f05",
            ]
        )
        .join(
            [
                "888e8a5e-da7f-11eb-9782-97fc8494b14e",
                "89c411f0-da7f-11eb-a0e4-a3451dad6f05",
            ]
        )
    )

    assert "add" in batch_action
    assert len(batch_action["add"]) == 2
    assert all(member["role"] == rolestr for member in batch_action["add"])

    assert "accept" in batch_action
    assert len(batch_action["accept"]) == 1

    assert "invite" in batch_action
    assert len(batch_action["invite"]) == 2

    assert "join" in batch_action
    assert len(batch_action["invite"]) == 2
