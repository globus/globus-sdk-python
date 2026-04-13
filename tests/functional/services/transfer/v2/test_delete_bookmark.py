from globus_sdk.testing import get_last_request, load_response


def test_delete_bookmark(client):
    meta = load_response(client.delete_bookmark).metadata

    res = client.delete_bookmark(meta["bookmark_id"])

    assert res.http_status == 200

    req = get_last_request()
    assert req.body is None
