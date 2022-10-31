import json

from globus_sdk import (
    GroupMemberVisibility,
    GroupPolicies,
    GroupRequiredSignupFields,
    GroupVisibility,
)
from globus_sdk._testing import get_last_request
from tests.common import register_api_route_fixture_file


def test_set_group_policies(groups_manager):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556/policies",
        "set_group_policies.json",
        method="PUT",
    )
    resp = groups_manager.set_group_policies(
        "d3974728-6458-11e4-b72d-123139141556",
        is_high_assurance=False,
        group_visibility=GroupVisibility.private,
        group_members_visibility=GroupMemberVisibility.managers,
        join_requests=False,
        signup_fields=[GroupRequiredSignupFields.address1],
        authentication_assurance_timeout=28800,
    )
    assert resp.http_status == 200
    assert "address1" in resp.data["signup_fields"]
    # ensure enums were stringified correctly
    req = get_last_request()
    req_body = json.loads(req.body)
    assert req_body["group_visibility"] == "private"
    assert req_body["group_members_visibility"] == "managers"
    assert req_body["signup_fields"] == ["address1"]


def test_set_group_policies_explicit_payload(groups_client):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556/policies",
        "set_group_policies.json",
        method="PUT",
    )
    # same payload as the above test, but formulated without GroupsManager
    payload = GroupPolicies(
        is_high_assurance=False,
        group_visibility=GroupVisibility.private,
        group_members_visibility=GroupMemberVisibility.managers,
        join_requests=False,
        signup_fields=[GroupRequiredSignupFields.address1],
        authentication_assurance_timeout=28800,
    )
    # set a string in the payload directly
    # this will pass through GroupPolicies.__setitem__
    payload["group_visibility"] = "authenticated"
    # now send it... (but ignore the response)
    groups_client.set_group_policies("d3974728-6458-11e4-b72d-123139141556", payload)
    # ensure enums were stringified correctly, but also that the raw string came through
    req = get_last_request()
    req_body = json.loads(req.body)
    assert req_body["group_visibility"] == "authenticated"
    assert req_body["group_members_visibility"] == "managers"
    assert req_body["signup_fields"] == ["address1"]
