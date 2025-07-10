import json
import urllib.parse

import pytest

from globus_sdk import MISSING
from globus_sdk.testing import get_last_request, load_response

_OMIT = object()


@pytest.mark.parametrize("local_user", ("my-user", MISSING, _OMIT))
def test_operation_rename(client, local_user):
    meta = load_response(client.operation_rename).metadata
    endpoint_id = meta["endpoint_id"]

    if local_user is not _OMIT:
        res = client.operation_rename(
            endpoint_id=endpoint_id,
            oldpath="~/old-name",
            newpath="~/new-name",
            local_user=local_user,
            query_params={"foo": "bar"},
        )
    else:
        res = client.operation_rename(
            endpoint_id=endpoint_id,
            oldpath="~/old-name",
            newpath="~/new-name",
            query_params={"foo": "bar"},
        )
    assert res["DATA_TYPE"] == "result"
    assert res["code"] == "FileRenamed"

    req = get_last_request()
    body = json.loads(req.body)
    assert body["old_path"] == "~/old-name"
    assert body["new_path"] == "~/new-name"
    if local_user not in (_OMIT, MISSING):
        assert body["local_user"] == local_user
    else:
        assert "local_user" not in body
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert query_params["foo"] == ["bar"]
