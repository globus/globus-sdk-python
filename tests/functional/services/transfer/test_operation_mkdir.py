import json
import urllib.parse

import pytest

from globus_sdk import MISSING
from globus_sdk._testing import get_last_request, load_response

_OMIT = object()


@pytest.mark.parametrize("local_user", ("my-user", MISSING, _OMIT))
def test_operation_mkdir(client, local_user):
    meta = load_response(client.operation_mkdir).metadata
    endpoint_id = meta["endpoint_id"]

    if local_user is not _OMIT:
        res = client.operation_mkdir(
            endpoint_id=endpoint_id,
            path="~/dir/",
            local_user=local_user,
            query_params={"foo": "bar"},
        )
    else:
        res = client.operation_mkdir(
            endpoint_id=endpoint_id,
            path="~/dir/",
            query_params={"foo": "bar"},
        )
    assert res["DATA_TYPE"] == "mkdir_result"
    assert res["code"] == "DirectoryCreated"

    req = get_last_request()
    body = json.loads(req.body)
    assert body["path"] == "~/dir/"
    if local_user not in (_OMIT, MISSING):
        assert body["local_user"] == local_user
    else:
        assert "local_user" not in body
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert query_params["foo"] == ["bar"]
