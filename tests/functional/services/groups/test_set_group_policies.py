import json

import pytest

from globus_sdk import (
    GroupMemberVisibility,
    GroupPolicies,
    GroupRequiredSignupFields,
    GroupVisibility,
)
from globus_sdk._testing import get_last_request, load_response


@pytest.mark.parametrize(
    "group_vis, group_member_vis, signup_fields, signup_fields_str",
    (
        (
            GroupVisibility.private,
            GroupMemberVisibility.members,
            [GroupRequiredSignupFields.address1],
            ["address1"],
        ),
        (
            GroupVisibility.authenticated,
            GroupMemberVisibility.managers,
            ["address1"],
            ["address1"],
        ),
        (
            "private",
            "members",
            [GroupRequiredSignupFields.address1, "address2"],
            ["address1", "address2"],
        ),
        ("authenticated", "managers", ["address1"], ["address1"]),
    ),
)
def test_set_group_policies(
    groups_manager,
    groups_client,
    group_vis,
    group_member_vis,
    signup_fields,
    signup_fields_str,
):
    group_vis_str = group_vis if isinstance(group_vis, str) else group_vis.value
    group_member_vis_str = (
        group_member_vis
        if isinstance(group_member_vis, str)
        else group_member_vis.value
    )

    meta = load_response(groups_client.set_group_policies).metadata

    resp = groups_manager.set_group_policies(
        meta["group_id"],
        is_high_assurance=False,
        group_visibility=group_vis,
        group_members_visibility=group_member_vis,
        join_requests=False,
        signup_fields=signup_fields,
        authentication_assurance_timeout=28800,
    )
    assert resp.http_status == 200
    assert "address1" in resp.data["signup_fields"]
    # ensure enums were stringified correctly
    req = get_last_request()
    req_body = json.loads(req.body)
    assert req_body["group_visibility"] == group_vis_str
    assert req_body["group_members_visibility"] == group_member_vis_str
    assert req_body["signup_fields"] == signup_fields_str


@pytest.mark.parametrize(
    "group_vis, group_member_vis, signup_fields, signup_fields_str",
    (
        (
            GroupVisibility.private,
            GroupMemberVisibility.members,
            [GroupRequiredSignupFields.address1],
            ["address1"],
        ),
        (
            GroupVisibility.authenticated,
            GroupMemberVisibility.managers,
            ["address1"],
            ["address1"],
        ),
        (
            "private",
            "members",
            [GroupRequiredSignupFields.address1, "address2"],
            ["address1", "address2"],
        ),
        ("authenticated", "managers", ["address1"], ["address1"]),
    ),
)
@pytest.mark.parametrize("setter_usage", (False, "enum", "str"))
def test_set_group_policies_explicit_payload(
    groups_client,
    group_vis,
    group_member_vis,
    signup_fields,
    signup_fields_str,
    setter_usage,
):
    group_vis_str = group_vis if isinstance(group_vis, str) else group_vis.value
    group_member_vis_str = (
        group_member_vis
        if isinstance(group_member_vis, str)
        else group_member_vis.value
    )

    meta = load_response(groups_client.set_group_policies).metadata

    # same payload as the above test, but formulated without GroupsManager
    payload = GroupPolicies(
        is_high_assurance=False,
        group_visibility=group_vis,
        group_members_visibility=group_member_vis,
        join_requests=False,
        signup_fields=signup_fields,
        authentication_assurance_timeout=28800,
    )
    if setter_usage:
        # set a string in the payload directly
        # this will pass through GroupPolicies.__setitem__
        if setter_usage == "enum":
            payload["group_visibility"] = group_vis
        elif setter_usage == "str":
            payload["group_visibility"] = group_vis_str
        else:
            raise NotImplementedError
    # now send it... (but ignore the response)
    groups_client.set_group_policies(meta["group_id"], payload)
    # ensure enums were stringified correctly, but also that the raw string came through
    req = get_last_request()
    req_body = json.loads(req.body)
    assert req_body["group_visibility"] == group_vis_str
    assert req_body["group_members_visibility"] == group_member_vis_str
    assert req_body["signup_fields"] == signup_fields_str
