import base64

import pytest

from globus_sdk.authorizers import BasicAuthorizer

USERNAME = "testUser"
PASSWORD = "PASSWORD"


@pytest.fixture
def authorizer():
    return BasicAuthorizer(USERNAME, PASSWORD)


def test_get_authorization_header(authorizer):
    """
    Gets authorization header, confirms expected value
    """
    header_val = authorizer.get_authorization_header()
    assert header_val[:6] == "Basic "
    decoded = base64.b64decode(header_val[6:].encode("utf-8")).decode("utf-8")
    assert decoded == f"{USERNAME}:{PASSWORD}"


def test_handle_missing_authorization(authorizer):
    """
    Confirms that BasicAuthorizer doesn't handle missing authorization
    """
    assert not authorizer.handle_missing_authorization()


@pytest.mark.parametrize(
    "username, password", [("user", "テスト"), ("дум", "pass"), ("テスト", "дум")]
)
def test_unicode_handling(username, password):
    """
    With a unicode string for the password, set and verify the
    Authorization header.
    """
    authorizer = BasicAuthorizer(username, password)
    header_val = authorizer.get_authorization_header()

    assert header_val[:6] == "Basic "
    decoded = base64.b64decode(header_val[6:].encode("utf-8")).decode("utf-8")
    assert decoded == f"{username}:{password}"
