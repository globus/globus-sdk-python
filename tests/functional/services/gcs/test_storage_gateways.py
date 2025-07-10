import urllib.parse

import pytest

import globus_sdk
from globus_sdk import MISSING
from globus_sdk.testing import get_last_request, load_response


@pytest.mark.parametrize(
    "include_param",
    [MISSING, "private_policies", "private_policies,foo", ("private_policies", "foo")],
)
def test_get_storage_gateway_list(client, include_param):
    meta = load_response(client.get_storage_gateway_list).metadata
    expect_ids = meta["ids"]

    res = client.get_storage_gateway_list(include=include_param)
    assert res.http_status == 200

    # confirm iterable and sanity check some fields
    assert len(list(res)) > 0
    for sg in res:
        assert sg["DATA_TYPE"] == "storage_gateway#1.0.0"
        assert "id" in sg
        assert "display_name" in sg
    assert [sg["id"] for sg in res] == expect_ids

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    if include_param is MISSING:
        assert parsed_qs == {}
    elif isinstance(include_param, str):
        assert parsed_qs == {"include": [include_param]}
    else:
        assert parsed_qs == {"include": [",".join(include_param)]}


def test_create_storage_gateway(client):
    meta = load_response(client.create_storage_gateway).metadata

    # the SDK does not validate the create document, so an empty document is fine, if
    # unrealistic, with a mocked response
    res = client.create_storage_gateway({})
    assert res.http_status == 200

    # confirm top level access to storage gateway data
    assert res["id"] == meta["id"]
    assert res["display_name"] == meta["display_name"]


def test_create_storage_gateway_validation_error(client):
    meta = load_response(
        client.create_storage_gateway, case="validation_error"
    ).metadata

    with pytest.raises(globus_sdk.GCSAPIError) as excinfo:
        client.create_storage_gateway({})

    error = excinfo.value
    assert error.http_status == meta["http_status"]
    assert error.code == meta["code"]
    assert error.message == meta["message"]


@pytest.mark.parametrize(
    "include_param",
    [MISSING, "private_policies", "private_policies,foo", ("private_policies", "foo")],
)
def test_get_storage_gateway(client, include_param):
    meta = load_response(client.get_storage_gateway).metadata

    res = client.get_storage_gateway(meta["id"], include=include_param)
    assert res.http_status == 200

    # confirm top level access to storage gateway data
    assert res["id"] == meta["id"]
    assert res["display_name"] == meta["display_name"]

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    if include_param is MISSING:
        assert parsed_qs == {}
    elif isinstance(include_param, str):
        assert parsed_qs == {"include": [include_param]}
    else:
        assert parsed_qs == {"include": [",".join(include_param)]}


def test_update_storage_gateway(client):
    meta = load_response(client.update_storage_gateway).metadata

    # as in the create test, an empty update document is not very realistic
    # but because there's no request validation, this is fine
    res = client.update_storage_gateway(meta["id"], {})
    assert res.http_status == 200

    # confirm top level access to response data
    assert res["code"] == "success"
    assert res["message"] == "Operation successful"


def test_delete_storage_gateway(client):
    meta = load_response(client.delete_storage_gateway).metadata

    res = client.delete_storage_gateway(meta["id"])
    assert res.http_status == 200

    # confirm top level access to response data
    assert res["code"] == "success"
    assert res["message"] == "Operation successful"


def test_delete_storage_gateway_permission_denied(client):
    meta = load_response(
        client.delete_storage_gateway, case="permission_denied_error"
    ).metadata

    with pytest.raises(globus_sdk.GCSAPIError) as excinfo:
        client.delete_storage_gateway(meta["id"])

    error = excinfo.value
    assert error.http_status == meta["http_status"]
    assert error.code == meta["code"]
    assert error.message == meta["message"]
