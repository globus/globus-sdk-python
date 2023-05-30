import json
import urllib.parse

from globus_sdk._testing import get_last_request, load_response


def test_operation_mkdir(client):
    meta = load_response(client.operation_mkdir).metadata
    endpoint_id = meta["endpoint_id"]

    res = client.operation_mkdir(
        endpoint_id=endpoint_id,
        path="~/dir/",
        local_user="my-user",
        query_params={"foo": "bar"},
    )
    assert res["DATA_TYPE"] == "mkdir_result"
    assert res["code"] == "DirectoryCreated"

    req = get_last_request()
    body = json.loads(req.body)
    assert body["path"] == "~/dir/"
    assert body["local_user"] == "my-user"
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert query_params["foo"] == ["bar"]
