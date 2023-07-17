from globus_sdk._testing import load_response


def test_create_index(client):
    meta = load_response(client.create_index).metadata

    res = client.create_index("Foo Title", "bar description")
    assert res.http_status == 200
    assert res["id"] == meta["index_id"]
