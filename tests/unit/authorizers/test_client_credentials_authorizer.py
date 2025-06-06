from unittest import mock

import pytest

from globus_sdk.authorizers import ClientCredentialsAuthorizer
from globus_sdk.scopes import Scope

ACCESS_TOKEN = "access_token_1"
EXPIRES_AT = -1
SCOPES = "scopes"


@pytest.fixture
def response():
    r = mock.Mock()
    r.by_resource_server = {
        "rs1": {"expires_at_seconds": -1, "access_token": "access_token_2"}
    }
    return r


@pytest.fixture
def client(response):
    c = mock.Mock()
    c.oauth2_client_credentials_tokens = mock.Mock(return_value=response)
    return c


@pytest.fixture
def authorizer(client):
    return ClientCredentialsAuthorizer(
        client, SCOPES, access_token=ACCESS_TOKEN, expires_at=EXPIRES_AT
    )


def test_get_token_response(authorizer, response, client):
    """
    Calls _get_token_response, confirms that the mock
    ConfidentialAppAuthClient is used and the known data was returned.
    """
    res = authorizer._get_token_response()
    assert res == response
    client.oauth2_client_credentials_tokens.assert_called_once_with(
        requested_scopes=SCOPES
    )


def test_multiple_resource_servers(authorizer, response):
    """
    Sets the mock ConfidentialAppAuthClient to return multiple resource
    servers. Confirms GlobusError is raised when _extract_token_data is
    called.
    """
    response.by_resource_server["rs2"] = {
        "expires_at_seconds": -1,
        "access_token": "access_token_3",
    }
    with pytest.raises(ValueError) as excinfo:
        authorizer._extract_token_data(response)

    assert "didn't return exactly one token" in str(excinfo.value)
    assert SCOPES in str(excinfo.value)


def test_can_create_authorizer_from_scope_objects(client):
    a1 = ClientCredentialsAuthorizer(client, Scope("foo"))
    assert a1.scopes == "foo"

    a2 = ClientCredentialsAuthorizer(
        client, [Scope("foo"), "bar", Scope("baz").with_dependency("buzz")]
    )
    assert a2.scopes == "foo bar baz[buzz]"
