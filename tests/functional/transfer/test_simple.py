import json
import urllib.parse
import uuid

import pytest

import globus_sdk
from globus_sdk._testing import get_last_request
from tests.common import (
    GO_EP1_ID,
    GO_EP1_SERVER_ID,
    GO_EP2_ID,
    register_api_route_fixture_file,
)


def test_get_endpoint(client):
    """
    Gets endpoint on go#ep1 and go#ep2, validate results
    """
    # register get_endpoint mock data
    register_api_route_fixture_file(
        "transfer", f"/endpoint/{GO_EP1_ID}", "get_endpoint_goep1.json"
    )
    register_api_route_fixture_file(
        "transfer", f"/endpoint/{GO_EP2_ID}", "get_endpoint_goep2.json"
    )

    # load the tutorial endpoint documents
    ep1_doc = client.get_endpoint(GO_EP1_ID)
    ep2_doc = client.get_endpoint(GO_EP2_ID)

    # check that their contents are at least basically sane (i.e. we didn't
    # get empty dicts or something)
    assert "display_name" in ep1_doc
    assert "display_name" in ep2_doc
    assert "canonical_name" in ep1_doc
    assert "canonical_name" in ep2_doc

    # double check a couple of fields, consider this done
    assert ep1_doc["canonical_name"] == "go#ep1"
    assert ep1_doc["DATA"][0]["id"] == GO_EP1_SERVER_ID
    assert ep2_doc["canonical_name"] == "go#ep2"


def test_update_endpoint(client):
    epid = uuid.uuid1()
    register_api_route_fixture_file(
        "transfer", f"/endpoint/{epid}", "ep_update.json", method="PUT"
    )

    # NOTE: pass epid as UUID, not str
    # requires that TransferClient correctly translates it
    update_data = {"display_name": "Updated Name", "description": "Updated description"}
    update_doc = client.update_endpoint(epid, update_data)

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
    epid = "example-id"
    register_api_route_fixture_file(
        "transfer", f"/endpoint/{epid}", "ep_create.json", method="PUT"
    )

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
    register_api_route_fixture_file(
        "transfer", "/endpoint", "ep_create.json", method="POST"
    )

    create_data = {"display_name": "Name", "description": "desc"}
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
        client.create_endpoint(create_data)

    assert "either MyProxy or OAuth, not both" in str(excinfo.value)


def test_operation_ls(client):
    """
    Does an `ls` on go#ep1, validate results, and check that the request parameters were
    formatted and sent correctly.
    """
    # register get_endpoint mock data
    register_api_route_fixture_file(
        "transfer", f"/operation/endpoint/{GO_EP1_ID}/ls", "operation_ls_goep1.json"
    )
    ls_path = f"https://transfer.api.globus.org/v0.10/operation/endpoint/{GO_EP1_ID}/ls"

    # load the tutorial endpoint ls doc
    ls_doc = client.operation_ls(GO_EP1_ID)

    # check that the result is an iterable of file and dir dict objects
    count = 0
    for x in ls_doc:
        assert "DATA_TYPE" in x
        assert x["DATA_TYPE"] in ("file", "dir")
        count += 1
    # not exact, just make sure the fixture wasn't empty
    assert count > 3

    req = get_last_request()
    assert req.url == ls_path

    # don't change the registered response
    # the resulting data might be "wrong", but we're just checking request formatting

    # orderby with a single str
    client.operation_ls(GO_EP1_ID, orderby="name")
    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert parsed_qs == {"orderby": ["name"]}

    # orderby multiple strs
    client.operation_ls(GO_EP1_ID, orderby=["size DESC", "name", "type"])
    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert parsed_qs == {"orderby": ["size DESC,name,type"]}

    # orderby + filter
    client.operation_ls(GO_EP1_ID, orderby="name", filter="name:~*.png")
    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert parsed_qs == {"orderby": ["name"], "filter": ["name:~*.png"]}


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
    res = client.endpoint_autoactivate(GO_EP1_ID, if_expires_in=300)
    assert res["code"] == "AlreadyActivated"

    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert parsed_qs == {"if_expires_in": ["300"]}


@pytest.mark.parametrize(
    "client_kwargs, qs",
    [
        ({}, {}),
        ({"query_params": {"foo": "bar"}}, {"foo": "bar"}),
        ({"filter": "foo"}, {"filter": "foo"}),
        ({"limit": 10, "offset": 100}, {"limit": "10", "offset": "100"}),
        ({"limit": 10, "query_params": {"limit": 100}}, {"limit": "10"}),
        ({"filter": "foo:bar:baz"}, {"filter": "foo:bar:baz"}),
        ({"filter": {"foo": "bar", "bar": "baz"}}, {"filter": "foo:bar/bar:baz"}),
        ({"filter": {"foo": ["bar", "baz"]}}, {"filter": "foo:bar,baz"}),
    ],
)
def test_task_list(client, client_kwargs, qs):
    register_api_route_fixture_file("transfer", "/task_list", "task_list.json")
    client.task_list(**client_kwargs)

    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    # parsed_qs will have each value as a list (because query-params are a multidict)
    # so transform the test data to match before comparison
    assert parsed_qs == {k: [v] for k, v in qs.items()}
