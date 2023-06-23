from globus_sdk._testing import load_response


def test_get_projects(client):
    meta = load_response(client.get_projects).metadata
    res = client.get_projects()

    assert [x["id"] for x in res] == meta["project_ids"]
