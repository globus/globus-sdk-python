from globus_sdk.testing import get_last_request, load_response


def test_get_bookmark(client):
    meta = load_response(client.get_bookmark).metadata

    res = client.get_bookmark(
        meta["bookmark_id"], query_params={"include": "collection"}
    )

    assert res.http_status == 200
    assert res["data"]["type"] == "Bookmark"
    assert res["data"]["id"] == meta["bookmark_id"]
    assert (
        res["data"]["relationships"]["collection"]["data"]["id"] == meta["collection"]
    )

    req = get_last_request()
    assert "include=collection" in req.url
    assert req.body is None
