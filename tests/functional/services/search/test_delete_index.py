import pytest

import globus_sdk
from globus_sdk.testing import load_response


def test_delete_index(client):
    meta = load_response(client.delete_index).metadata

    res = client.delete_index(meta["index_id"])
    assert res.http_status == 200
    assert res["acknowledged"] is True


def test_delete_index_delete_already_pending(client):
    meta = load_response(client.delete_index, case="delete_pending").metadata

    with pytest.raises(globus_sdk.SearchAPIError) as excinfo:
        client.delete_index(meta["index_id"])

    err = excinfo.value

    assert err.http_status == 409
    assert err.code == "Conflict.IncompatibleIndexStatus"
