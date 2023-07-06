from globus_sdk._testing import load_response


def test_delete_project(client):
    meta = load_response(client.delete_project).metadata

    project_id = meta["id"]
    res = client.delete_project(project_id)

    assert res["project"]["id"] == meta["id"]
