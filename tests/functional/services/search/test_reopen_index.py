from globus_sdk._testing import load_response


def test_reopen_index(client):
    meta = load_response(client.reopen_index).metadata

    res = client.reopen_index(meta["index_id"])
    assert res.http_status == 200
    assert res["acknowledged"] is True
