from globus_sdk.testing import get_last_request, load_response


def test_list_bookmarks(client):
    meta = load_response(client.list_bookmarks).metadata

    res = client.list_bookmarks(
        query_params={"include": "collection"},
    )

    assert res.http_status == 200
    for i, bm in enumerate(res["data"]):
        assert bm["type"] == "Bookmark"
        assert bm["id"] == meta["bookmarks"][i]["bookmark_id"]
        assert bm["attributes"]["name"] == meta["bookmarks"][i]["name"]
        assert bm["attributes"]["path"] == meta["bookmarks"][i]["path"]
        assert bm["attributes"]["pinned"] == meta["bookmarks"][i]["pinned"]

        assert (
            bm["relationships"]["collection"]["data"]["id"]
            == meta["bookmarks"][i]["collection_id"]
        )

    for i, col in enumerate(res["included"]):
        assert col["type"] == "Collection"
        assert col["id"] == meta["bookmarks"][i]["collection_id"]

    req = get_last_request()
    assert "include=collection" in req.url
    assert req.body is None
