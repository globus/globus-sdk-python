import urllib.parse
import uuid

import pytest

import globus_sdk
from globus_sdk._testing import get_last_request, load_response


@pytest.fixture
def client_id():
    return str(uuid.uuid4())


@pytest.fixture
def base_client(client_id):
    return globus_sdk.AuthClient(client_id=client_id)


@pytest.fixture
def confidential_client(client_id):
    return globus_sdk.ConfidentialAppAuthClient(
        client_id=client_id, client_secret="somesecret"
    )


def test_oauth2_revoke_token_works(client_id, base_client):
    load_response(base_client.oauth2_revoke_token)
    response = base_client.oauth2_revoke_token("sometoken")
    assert response["active"] is False
    lastreq = get_last_request()
    body = lastreq.body
    assert body != ""
    parsed_body = urllib.parse.parse_qs(body)
    assert parsed_body == {"token": ["sometoken"], "client_id": [client_id]}


def test_oauth2_revoke_token_does_not_send_client_id_when_authenticated(
    client_id,
    confidential_client,
):
    load_response(confidential_client.oauth2_revoke_token)
    response = confidential_client.oauth2_revoke_token("sometoken")
    assert response["active"] is False
    lastreq = get_last_request()
    body = lastreq.body
    assert body != ""
    parsed_body = urllib.parse.parse_qs(body)
    assert parsed_body == {"token": ["sometoken"]}
