import json

from globus_sdk.experimental import BookmarkUpdateDocument
from globus_sdk.testing import get_last_request, load_response


def test_update_bookmark(client):
    meta = load_response(client.update_bookmark).metadata

    data = BookmarkUpdateDocument(
        meta["name"],
        meta["path"],
        pinned=meta["pinned"],
    )

    res = client.update_bookmark(meta["bookmark_id"], data)

    assert res.http_status == 200
    assert res["data"]["type"] == "Bookmark"
    assert (
        res["data"]["relationships"]["collection"]["data"]["id"] == meta["collection"]
    )

    req = get_last_request()
    sent = json.loads(req.body)
    assert sent["data"]["attributes"]["name"] == meta["name"]
    assert sent["data"]["attributes"]["path"] == meta["path"]
    assert sent["data"]["attributes"]["pinned"] == meta["pinned"]
