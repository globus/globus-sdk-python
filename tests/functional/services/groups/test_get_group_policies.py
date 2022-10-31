from tests.common import register_api_route_fixture_file


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
