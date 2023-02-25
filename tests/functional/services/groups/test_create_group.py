import json

from globus_sdk._testing import get_last_request, load_response


def test_create_group(groups_client):
    meta = load_response(groups_client.create_group).metadata
    res = groups_client.create_group(
        {"name": "Claptrap's Rough Riders", "description": "No stairs allowed."}
    )

    assert res.http_status == 200
    assert "Claptrap" in res["name"]
    assert "No stairs allowed." in res["description"]
    assert res["id"] == meta["group_id"]

    req = get_last_request()
    req_body = json.loads(req.body)
    assert req_body["description"] == "No stairs allowed."


def test_create_group_via_manager(groups_manager, groups_client):
    meta = load_response(groups_client.create_group).metadata
    res = groups_manager.create_group(
        name="Claptrap's Rough Riders", description="No stairs allowed."
    )

    assert res.http_status == 200
    assert "Claptrap" in res["name"]
    assert "No stairs allowed." in res["description"]
    assert res["id"] == meta["group_id"]

    req = get_last_request()
    req_body = json.loads(req.body)
    assert req_body["description"] == "No stairs allowed."
