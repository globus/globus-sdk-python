from unittest import mock

import pytest

from globus_sdk.authorizers import RefreshTokenAuthorizer

REFRESH_TOKEN = "refresh_token_1"
ACCESS_TOKEN = "access_token_1"
EXPIRES_AT = -1


@pytest.fixture(params=["simple", "with_new_refresh_token"])
def response(request):
    r = mock.Mock()
    r.by_resource_server = {
        "simple": {"rs1": {"expires_at_seconds": -1, "access_token": "access_token_2"}},
        "with_new_refresh_token": {
            "rs1": {
                "expires_at_seconds": -1,
                "access_token": "access_token_2",
                "refresh_token": "refresh_token_2",
            }
        },
    }[request.param]
    return r


@pytest.fixture
def client(response):
    c = mock.Mock()
    c.oauth2_refresh_token = mock.Mock(return_value=response)
    return c


@pytest.fixture
def authorizer(client):
    return RefreshTokenAuthorizer(
        REFRESH_TOKEN, client, access_token=ACCESS_TOKEN, expires_at=EXPIRES_AT
    )


def test_get_token_response(authorizer, client, response):
    """
    Calls _get_token_response, confirms that the mock
    AuthClient is used and the known data was returned.
    """
    # get new_access_token
    res = authorizer._get_token_response()
    assert res == response
    # confirm mock ConfidentialAppAuthClient was used as expected
    client.oauth2_refresh_token.assert_called_once_with(REFRESH_TOKEN)


def test_multiple_resource_servers(authorizer, response):
    """
    Sets the mock client to return multiple resource servers.
    Confirms GlobusError is raised when _extract_token_data is called.
    """
    response.by_resource_server["rs2"] = {
        "expires_at_seconds": -1,
        "access_token": "access_token_3",
    }
    with pytest.raises(ValueError) as excinfo:
        authorizer._extract_token_data(response)
    assert "didn't return exactly one token" in str(excinfo.value)


def test_conditional_refresh_token_update(authorizer, response):
    """
    Call ensure_valid_token (triggering a refresh)
    Confirm that the authorizer always updates its access token and only updates
    refresh_token if one was present in the response
    """
    authorizer.ensure_valid_token()  # trigger refresh
    token_data = response.by_resource_server["rs1"]
    if "refresh_token" in token_data:  # if present, confirm refresh token was updated
        assert authorizer.access_token == "access_token_2"
        assert authorizer.refresh_token == "refresh_token_2"
    else:  # otherwise, confirm no change
        assert authorizer.access_token == "access_token_2"
        assert authorizer.refresh_token == "refresh_token_1"
