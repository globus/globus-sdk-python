import json
import uuid

import pytest

from globus_sdk._testing import get_last_request, load_response


@pytest.mark.parametrize(
    "admin_id_style", ("none", "string", "list", "set", "uuid", "uuid_list")
)
def test_update_project_admin_id_styles(client, admin_id_style):
    meta = load_response(client.update_project).metadata

    if admin_id_style == "none":
        admin_ids = None
    elif admin_id_style == "string":
        admin_ids = meta["admin_id"]
    elif admin_id_style == "list":
        admin_ids = [meta["admin_id"]]
    elif admin_id_style == "set":
        admin_ids = {meta["admin_id"]}
    elif admin_id_style == "uuid":
        admin_ids = uuid.UUID(meta["admin_id"])
    elif admin_id_style == "uuid_list":
        admin_ids = [uuid.UUID(meta["admin_id"])]
    else:
        raise NotImplementedError(f"unknown admin_id_style {admin_id_style}")

    project_id = meta["id"]
    res = client.update_project(
        project_id, display_name="My Project", admin_ids=admin_ids
    )

    assert res["project"]["id"] == meta["id"]

    last_req = get_last_request()
    data = json.loads(last_req.body)
    assert list(data) == ["project"], data  # 'project' is the only key
    if admin_id_style == "none":
        assert data["project"] == {"display_name": "My Project"}
    else:
        assert data["project"] == {
            "display_name": "My Project",
            "admin_ids": [meta["admin_id"]],
        }


@pytest.mark.parametrize(
    "group_id_style", ("string", "list", "set", "uuid", "uuid_list")
)
def test_update_project_group_id_styles(client, group_id_style):
    meta = load_response(client.update_project, case="admin_group").metadata

    if group_id_style == "string":
        group_ids = meta["admin_group_id"]
    elif group_id_style == "list":
        group_ids = [meta["admin_group_id"]]
    elif group_id_style == "set":
        group_ids = {meta["admin_group_id"]}
    elif group_id_style == "uuid":
        group_ids = uuid.UUID(meta["admin_group_id"])
    elif group_id_style == "uuid_list":
        group_ids = [uuid.UUID(meta["admin_group_id"])]
    else:
        raise NotImplementedError(f"unknown group_id_style {group_id_style}")

    project_id = meta["id"]
    res = client.update_project(
        project_id, contact_email="support@globus.org", admin_group_ids=group_ids
    )

    assert res["project"]["id"] == meta["id"]

    last_req = get_last_request()
    data = json.loads(last_req.body)
    assert list(data) == ["project"], data  # 'project' is the only key
    assert data["project"] == {
        "contact_email": "support@globus.org",
        "admin_group_ids": [meta["admin_group_id"]],
    }
