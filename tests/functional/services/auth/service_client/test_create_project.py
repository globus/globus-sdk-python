import json
import uuid

import pytest

from globus_sdk.testing import get_last_request, load_response


@pytest.mark.parametrize(
    "admin_id_style", ("string", "list", "set", "uuid", "uuid_list")
)
def test_create_project_admin_id_styles(service_client, admin_id_style):
    meta = load_response(service_client.create_project).metadata

    if admin_id_style == "string":
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

    res = service_client.create_project(
        "My Project", "support@globus.org", admin_ids=admin_ids
    )

    assert res["project"]["id"] == meta["id"]

    last_req = get_last_request()
    data = json.loads(last_req.body)
    assert list(data) == ["project"], data  # 'project' is the only key
    assert data["project"]["display_name"] == "My Project", data
    assert data["project"]["contact_email"] == "support@globus.org", data
    assert data["project"]["admin_ids"] == [meta["admin_id"]], data
    assert "admin_group_ids" not in data["project"], data


@pytest.mark.parametrize(
    "group_id_style", ("string", "list", "set", "uuid", "uuid_list")
)
def test_create_project_group_id_styles(service_client, group_id_style):
    meta = load_response(service_client.create_project, case="admin_group").metadata

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

    res = service_client.create_project(
        "My Project", "support@globus.org", admin_group_ids=group_ids
    )

    assert res["project"]["id"] == meta["id"]

    last_req = get_last_request()
    data = json.loads(last_req.body)
    assert list(data) == ["project"], data  # 'project' is the only key
    assert data["project"]["display_name"] == "My Project", data
    assert data["project"]["contact_email"] == "support@globus.org", data
    assert data["project"]["admin_group_ids"] == [meta["admin_group_id"]], data
    assert "admin_ids" not in data["project"], data
