import json
import urllib.parse
import uuid

import pytest

import globus_sdk
import globus_sdk.exc
from globus_sdk._testing import get_last_request, load_response
from tests.common import GO_EP1_ID, register_api_route_fixture_file


def test_get_endpoint(client):
    """
    Gets endpoint on fixture, validate results
    """
    meta = load_response(client.get_endpoint).metadata
    epid = meta["endpoint_id"]

    # load the endpoint document
    ep_doc = client.get_endpoint(epid)

    # check that the contents are basically OK
    assert ep_doc["DATA_TYPE"] == "endpoint"
    assert ep_doc["id"] == epid
    assert "display_name" in ep_doc


@pytest.mark.parametrize("epid_type", [uuid.UUID, str])
def test_update_endpoint(epid_type, client):
    meta = load_response(client.update_endpoint).metadata
    epid = meta["endpoint_id"]

    # NOTE: pass epid as UUID or str
    # requires that TransferClient correctly translates UUID
    update_data = {"display_name": "Updated Name", "description": "Updated description"}
    update_doc = client.update_endpoint(epid_type(epid), update_data)

    # make sure response is a successful update
    assert update_doc["DATA_TYPE"] == "result"
    assert update_doc["code"] == "Updated"
    assert update_doc["message"] == "Endpoint updated successfully"

    req = get_last_request()
    assert json.loads(req.body) == update_data


def test_update_endpoint_rewrites_activation_servers(client):
    """
    Update endpoint, validate results
    """
    meta = load_response(client.update_endpoint).metadata
    epid = meta["endpoint_id"]

    # sending myproxy_server implicitly adds oauth_server=null
    update_data = {"myproxy_server": "foo"}
    client.update_endpoint(epid, update_data.copy())
    req = get_last_request()
    assert json.loads(req.body) != update_data
    update_data["oauth_server"] = None
    assert json.loads(req.body) == update_data

    # sending oauth_server implicitly adds myproxy_server=null
    update_data = {"oauth_server": "foo"}
    client.update_endpoint(epid, update_data.copy())
    req = get_last_request()
    assert json.loads(req.body) != update_data
    update_data["myproxy_server"] = None
    assert json.loads(req.body) == update_data


def test_update_endpoint_invalid_activation_servers(client):
    epid = "example-id"
    update_data = {"oauth_server": "foo", "myproxy_server": "bar"}
    with pytest.raises(globus_sdk.GlobusSDKUsageError) as excinfo:
        client.update_endpoint(epid, update_data)

    assert "either MyProxy or OAuth, not both" in str(excinfo.value)


def test_create_endpoint(client):
    load_response(client.create_endpoint)

    create_data = {"display_name": "Name", "description": "desc"}
    with pytest.warns(globus_sdk.exc.RemovedInV4Warning):
        create_doc = client.create_endpoint(create_data)

    # make sure response is a successful update
    assert create_doc["DATA_TYPE"] == "endpoint_create_result"
    assert create_doc["code"] == "Created"
    assert create_doc["message"] == "Endpoint created successfully"

    req = get_last_request()
    assert json.loads(req.body) == create_data


def test_create_endpoint_invalid_activation_servers(client):
    create_data = {"oauth_server": "foo", "myproxy_server": "bar"}
    with pytest.raises(globus_sdk.GlobusSDKUsageError) as excinfo:
        with pytest.warns(globus_sdk.exc.RemovedInV4Warning):
            client.create_endpoint(create_data)

    assert "either MyProxy or OAuth, not both" in str(excinfo.value)


def test_autoactivation(client):
    """
    Do `autoactivate` on go#ep1, validate results, and check that `if_expires_in` can be
    passed correctly.
    """
    # register get_endpoint mock data
    register_api_route_fixture_file(
        "transfer",
        f"/endpoint/{GO_EP1_ID}/autoactivate",
        "activation_stub.json",
        method="POST",
    )

    # load and check the activation doc
    with pytest.warns(globus_sdk.exc.RemovedInV4Warning):
        res = client.endpoint_autoactivate(GO_EP1_ID)
    assert res["code"] == "AutoActivated.CachedCredential"

    # check the formatted url for the request
    req = get_last_request()
    assert (
        req.url
        == f"https://transfer.api.globus.org/v0.10/endpoint/{GO_EP1_ID}/autoactivate"
    )

    register_api_route_fixture_file(
        "transfer",
        f"/endpoint/{GO_EP1_ID}/autoactivate",
        "activation_already_activated_stub.json",
        method="POST",
        replace=True,
    )
    with pytest.warns(globus_sdk.exc.RemovedInV4Warning):
        res = client.endpoint_autoactivate(GO_EP1_ID, if_expires_in=300)
    assert res["code"] == "AlreadyActivated"

    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert parsed_qs == {"if_expires_in": ["300"]}
