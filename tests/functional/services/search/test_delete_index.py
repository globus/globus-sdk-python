from globus_sdk._testing import load_response


def test_delete_index(client):
    meta = load_response(client.delete_index).metadata

    res = client.delete_index(meta["index_id"])
    assert res.http_status == 200
    assert res["acknowledged"] is True
