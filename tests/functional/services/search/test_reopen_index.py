import pytest

import globus_sdk
from globus_sdk._testing import load_response


def test_reopen_index(client):
    meta = load_response(client.reopen_index).metadata

    res = client.reopen_index(meta["index_id"])
    assert res.http_status == 200
    assert res["acknowledged"] is True


def test_reopen_index_already_open(client):
    meta = load_response(client.reopen_index, case="already_open").metadata

    with pytest.raises(globus_sdk.SearchAPIError) as excinfo:
        client.reopen_index(meta["index_id"])

    err = excinfo.value

    assert err.http_status == 409
    assert err.code == "Conflict.IncompatibleIndexStatus"
