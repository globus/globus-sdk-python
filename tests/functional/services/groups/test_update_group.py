from tests.common import register_api_route_fixture_file


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
