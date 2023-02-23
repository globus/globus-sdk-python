import urllib.parse

from globus_sdk._testing import get_last_request, load_response
from globus_sdk.scopes import MutableScope


def test_oauth2_client_credentials_tokens(auth_client):
    meta = load_response(auth_client.oauth2_client_credentials_tokens).metadata

    response = auth_client.oauth2_client_credentials_tokens(meta["scope"])
    assert (
        response.by_resource_server[meta["resource_server"]]["access_token"]
        == meta["access_token"]
    )


def test_oauth2_client_credentials_tokens_can_accept_mutable_scope_object(auth_client):
    meta = load_response(auth_client.oauth2_client_credentials_tokens).metadata

    response = auth_client.oauth2_client_credentials_tokens(MutableScope(meta["scope"]))
    assert (
        response.by_resource_server[meta["resource_server"]]["access_token"]
        == meta["access_token"]
    )

    last_req = get_last_request()
    assert last_req.body
    body = last_req.body
    assert body != ""
    parsed_body = urllib.parse.parse_qs(body)
    assert parsed_body["scope"] == [meta["scope"]]
