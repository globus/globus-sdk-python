from tests.common import register_api_route_fixture_file


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
