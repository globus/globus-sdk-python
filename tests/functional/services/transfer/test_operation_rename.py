import json
import urllib.parse

from globus_sdk._testing import get_last_request, load_response


def test_operation_rename(client):
    meta = load_response(client.operation_rename).metadata
    endpoint_id = meta["endpoint_id"]

    res = client.operation_rename(
        endpoint_id=endpoint_id,
        oldpath="~/old-name",
        newpath="~/new-name",
        local_user="my-user",
        query_params={"foo": "bar"},
    )
    assert res["DATA_TYPE"] == "result"
    assert res["code"] == "FileRenamed"

    req = get_last_request()
    body = json.loads(req.body)
    assert body["old_path"] == "~/old-name"
    assert body["new_path"] == "~/new-name"
    assert body["local_user"] == "my-user"
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert query_params["foo"] == ["bar"]
