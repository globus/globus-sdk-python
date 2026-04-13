import json

from globus_sdk.experimental import BookmarkCreateDocument
from globus_sdk.testing import get_last_request, load_response


def test_create_bookmark(client):
    meta = load_response(client.create_bookmark).metadata

    data = BookmarkCreateDocument(
        meta["collection"],
        meta["name"],
        meta["path"],
    )

    res = client.create_bookmark(data)

    assert res.http_status == 201
    assert res["data"]["type"] == "Bookmark"

    req = get_last_request()
    sent = json.loads(req.body)
    assert sent["data"]["attributes"]["name"] == meta["name"]
    assert sent["data"]["attributes"]["path"] == meta["path"]
    assert (
        sent["data"]["relationships"]["collection"]["data"]["id"] == meta["collection"]
    )
