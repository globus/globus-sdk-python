import json

import pytest

import globus_sdk
from globus_sdk.testing import get_last_request, load_response


@pytest.fixture
def search_client():
    client = globus_sdk.SearchClient()
    with client.retry_config.tune(max_retries=0):
        yield client


def test_search_role_create(search_client):
    meta = load_response(search_client.create_role).metadata
    send_data = {
        "role_name": meta["role_name"],
        "principal": "urn:globus:auth:identity:" + meta["identity_id"],
    }

    res = search_client.create_role(meta["index_id"], send_data)
    assert res.http_status == 200
    assert res["index_id"] == meta["index_id"]
    assert res["role_name"] == "writer"

    last_req = get_last_request()
    sent = json.loads(last_req.body)
    assert sent == send_data


def test_search_role_delete(search_client):
    meta = load_response(search_client.delete_role).metadata

    res = search_client.delete_role(meta["index_id"], meta["role_id"])
    assert res.http_status == 200
    assert res["success"] is True
    assert res["deleted"]["index_id"] == meta["index_id"]
    assert res["deleted"]["id"] == meta["role_id"]


def test_search_role_list(search_client):
    meta = load_response(search_client.get_role_list).metadata

    res = search_client.get_role_list(meta["index_id"])
    assert res.http_status == 200
    role_list = res["role_list"]
    assert isinstance(role_list, list)
    assert len(role_list) == 2
