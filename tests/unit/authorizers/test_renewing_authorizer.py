import time
from unittest import mock

import pytest

from globus_sdk import exc
from globus_sdk.authorizers.renewing import EXPIRES_ADJUST_SECONDS, RenewingAuthorizer


class MockRenewer(RenewingAuthorizer):
    """
    Class that implements RenewingAuthorizer so that _get_token_response and
    _extract_token_data can return known values for testing
    """

    def __init__(self, token_data, **kwargs):
        self.token_data = token_data
        self.token_response = mock.Mock()
        super().__init__(**kwargs)

    def _get_token_response(self):
        return self.token_response

    def _extract_token_data(self, res):
        return self.token_data


ACCESS_TOKEN = "access_token_1"


@pytest.fixture
def expires_at():
    return int(time.time()) + EXPIRES_ADJUST_SECONDS + 10


@pytest.fixture
def token_data():
    return {
        "expires_at_seconds": int(time.time()) + 1000,
        "access_token": "access_token_2",
    }


@pytest.fixture
def on_refresh():
    return mock.Mock()


@pytest.fixture
def authorizer(on_refresh, token_data, expires_at):
    return MockRenewer(
        token_data,
        access_token=ACCESS_TOKEN,
        expires_at=expires_at,
        on_refresh=on_refresh,
    )


@pytest.fixture
def expired_authorizer(on_refresh, token_data, expires_at):
    return MockRenewer(
        token_data,
        access_token=ACCESS_TOKEN,
        expires_at=expires_at - 11,
        on_refresh=on_refresh,
    )


def test_init(token_data, expires_at):
    """
    Creating a MockRenewer with partial data (expires_at, access_token) results in
    errors.
    Either complete data or no partial data works.
    """
    authorizer = MockRenewer(
        token_data, access_token=ACCESS_TOKEN, expires_at=expires_at
    )
    assert authorizer.access_token == ACCESS_TOKEN
    assert authorizer.access_token != token_data["access_token"]

    # with no args, an automatic "refresh" is triggered on init
    authorizer = MockRenewer(token_data)
    assert authorizer.access_token == token_data["access_token"]
    assert authorizer.expires_at == token_data["expires_at_seconds"]

    with pytest.raises(exc.GlobusSDKUsageError):
        MockRenewer(token_data, access_token=ACCESS_TOKEN)

    with pytest.raises(exc.GlobusSDKUsageError):
        MockRenewer(token_data, expires_at=expires_at)


def test_get_new_access_token(authorizer, token_data, on_refresh):
    """
    Calls get_new_access token, confirms that the mock _get_token_data
    is used and that the mock on_refresh function is called.
    """
    # take note of original access_token_hash
    original_hash = authorizer._access_token_hash

    # get new_access_token
    authorizer._get_new_access_token()
    # confirm side effects
    assert authorizer.access_token == token_data["access_token"]
    assert authorizer.expires_at == token_data["expires_at_seconds"]
    assert authorizer._access_token_hash != original_hash
    on_refresh.assert_called_once()


def test_ensure_valid_token_ok(authorizer):
    """
    Confirms nothing is done before the access_token expires,
    """
    authorizer.ensure_valid_token()
    assert authorizer.access_token == ACCESS_TOKEN


def test_ensure_valid_token_expired(expired_authorizer, token_data):
    """
    Confirms a new access_token is gotten after expiration
    """
    expired_authorizer.ensure_valid_token()
    assert expired_authorizer.access_token == token_data["access_token"]
    assert expired_authorizer.expires_at == token_data["expires_at_seconds"]


def test_ensure_valid_token_no_token(authorizer, token_data):
    """
    Confirms a new access_token is gotten if the old one is set to None
    """
    authorizer.access_token = None
    authorizer.ensure_valid_token()
    assert authorizer.access_token == token_data["access_token"]
    assert authorizer.expires_at == token_data["expires_at_seconds"]


def test_ensure_valid_token_no_expiration(authorizer, token_data):
    """
    Confirms a new access_token is gotten if expires_at is set to None
    """
    authorizer.expires_at = None
    authorizer.ensure_valid_token()
    assert authorizer.access_token == token_data["access_token"]
    assert authorizer.expires_at == token_data["expires_at_seconds"]


def test_get_authorization_header(authorizer):
    """
    Gets authorization header, confirms expected value
    """
    assert authorizer.get_authorization_header() == "Bearer " + ACCESS_TOKEN


def test_get_authorization_header_expired(expired_authorizer, token_data):
    """
    Sets the access_token to be expired, then gets authorization header
    Confirms header value uses the new access_token.
    """
    assert expired_authorizer.get_authorization_header() == (
        "Bearer " + token_data["access_token"]
    )


def test_get_authorization_header_no_token(authorizer, token_data):
    """
    Sets the access_token to None, then gets authorization header
    Confirms header value uses the new access_token.
    """
    authorizer.access_token = None
    assert authorizer.get_authorization_header() == (
        "Bearer " + token_data["access_token"]
    )


def test_get_authorization_header_no_expires(authorizer, token_data):
    """
    Sets expires_at to None, then gets authorization header
    Confirms header value uses the new access_token.
    """
    authorizer.expires_at = None
    assert authorizer.get_authorization_header() == (
        "Bearer " + token_data["access_token"]
    )


def test_handle_missing_authorization(authorizer):
    """
    Confirms that RenewingAuthorizers will attempt to fix 401s
    by treating their existing access_token as expired
    """
    assert authorizer.handle_missing_authorization()
    assert authorizer.expires_at is None
