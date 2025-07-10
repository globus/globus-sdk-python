from globus_sdk.testing import load_response


def test_delete_project(service_client):
    meta = load_response(service_client.delete_project).metadata

    project_id = meta["id"]
    res = service_client.delete_project(project_id)

    assert res["project"]["id"] == meta["id"]
