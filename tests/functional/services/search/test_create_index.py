import pytest

import globus_sdk
from globus_sdk.testing import load_response


def test_create_index(client):
    meta = load_response(client.create_index).metadata

    res = client.create_index("Foo Title", "bar description")
    assert res.http_status == 200
    assert res["id"] == meta["index_id"]


def test_create_index_limit_exceeded(client):
    load_response(client.create_index, case="trial_limit")

    with pytest.raises(globus_sdk.SearchAPIError) as excinfo:
        client.create_index("Foo Title", "bar description")

    err = excinfo.value

    assert err.http_status == 409
    assert err.code == "Conflict.LimitExceeded"
