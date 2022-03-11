import json
import urllib.parse

import pytest

from globus_sdk import (
    GroupMemberVisibility,
    GroupPolicies,
    GroupRequiredSignupFields,
    GroupVisibility,
)
from globus_sdk._testing import get_last_request, load_response
from tests.common import register_api_route_fixture_file


def test_my_groups_simple(groups_client):
    register_api_route_fixture_file("groups", "/v2/groups/my_groups", "my_groups.json")

    res = groups_client.get_my_groups()
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, list)
    assert "duke" in [g["name"] for g in data]


def test_get_group(groups_client):
    meta = load_response(groups_client.get_group).metadata

    res = groups_client.get_group(group_id=meta["group_id"])
    assert res.http_status == 200
    assert "Claptrap" in res["name"]


@pytest.mark.parametrize(
    "include_param",
    ["policies", "policies,memberships", ["memberships", "policies", "child_ids"]],
)
def test_get_group_include(groups_client, include_param):
    meta = load_response(groups_client.get_group).metadata
    expect_param = (
        ",".join(include_param) if not isinstance(include_param, str) else include_param
    )

    res = groups_client.get_group(group_id=meta["group_id"], include=include_param)
    assert res.http_status == 200
    assert "Claptrap" in res["name"]

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert len(parsed_qs["include"]) == 1
    assert parsed_qs["include"][0] == expect_param


def test_delete_group(groups_client):
    meta = load_response(groups_client.delete_group).metadata

    res = groups_client.delete_group(group_id=meta["group_id"])
    assert res.http_status == 200
    assert "Claptrap" in res["name"]


def test_create_group(groups_manager):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups",
        "created_group.json",
        method="POST",
    )

    res = groups_manager.create_group(
        name="Claptrap's Rough Riders", description="No stairs allowed."
    )
    assert res.http_status == 200
    assert "Claptrap" in res.data["name"]
    assert "No stairs allowed." in res.data["description"]


def test_update_group(groups_client):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/592e0566-5201-4207-b5e1-7cd6c516e9a0",
        "updated_group.json",
        method="PUT",
    )

    data = {
        "name": "Claptrap's Rough Riders",
        "description": "Stairs strongly discouraged.",
    }
    res = groups_client.update_group(
        group_id="592e0566-5201-4207-b5e1-7cd6c516e9a0", data=data
    )
    assert res.http_status == 200
    assert "Claptrap" in res.data["name"]
    assert "Stairs strongly discouraged." in res.data["description"]


def test_get_group_policies(groups_client):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556/policies",
        "get_group_policies.json",
    )
    resp = groups_client.get_group_policies("d3974728-6458-11e4-b72d-123139141556")
    assert resp.http_status == 200
    assert resp.data == {
        "is_high_assurance": False,
        "authentication_assurance_timeout": 28800,
        "group_visibility": "private",
        "group_members_visibility": "managers",
        "join_requests": False,
        "signup_fields": [],
    }


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
