from globus_sdk.testing import load_response


def test_get_projects(service_client):
    meta = load_response(service_client.get_projects).metadata
    res = service_client.get_projects()

    assert [x["id"] for x in res] == meta["project_ids"]
