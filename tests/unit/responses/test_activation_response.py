import json
import time
from unittest import mock

import pytest
import requests

from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.transfer.response import ActivationRequirementsResponse


def make_response(
    activated=True,
    expires_in=0,
    auto_activation_supported=True,
    oauth_server=None,
    DATA=None,
):
    """
    Helper for making ActivationRequirementsResponses with known fields
    """
    DATA = DATA or []
    data = {
        "activated": activated,
        "expires_in": expires_in,
        "oauth_server": oauth_server,
        "DATA": DATA,
        "auto_activation_supported": auto_activation_supported,
    }
    response = requests.Response()
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps(data).encode("utf-8")
    return ActivationRequirementsResponse(
        GlobusHTTPResponse(response, client=mock.Mock())
    )


def test_expires_at():
    """
    Confirms expires_at is set properly by __init__
    """
    for seconds in [0, 10, 100, 1000, -10]:
        response = make_response(expires_in=seconds)
        expected = int(time.time()) + seconds
        # make sure within a 1 second range of expected value
        assert response.expires_at in (expected - 1, expected, expected + 1)

    # -1 marks no expiration
    response = make_response(expires_in=-1)
    assert response.expires_at is None


@pytest.mark.parametrize("value", (True, False))
def test_supports_auto_activation(value):
    """
    Gets supports_auto_activation from made responses, validates results
    """
    response = make_response(auto_activation_supported=value)
    assert response.supports_auto_activation == value


def test_supports_web_activation():
    """
    Gets supports_web_activation from made responses, validates results
    """
    # true if auto_activatable,
    response = make_response(auto_activation_supported=True)
    assert response.supports_web_activation
    # has an oauth server,
    response = make_response(auto_activation_supported=False, oauth_server="server")
    assert response.supports_web_activation
    # or one of the other documents is myproxy or delegate_myproxy,
    response = make_response(
        auto_activation_supported=False, DATA=[{"type": "myproxy"}]
    )
    assert response.supports_web_activation
    response = make_response(
        auto_activation_supported=False, DATA=[{"type": "delegate_myproxy"}]
    )
    assert response.supports_web_activation

    # otherwise false
    response = make_response(auto_activation_supported=False)
    assert not response.supports_web_activation


def test_active_until():
    """
    Calls active_until on made responses, validates results
    """
    # not active at all
    response = make_response(activated=False)
    assert not response.active_until(0)

    # always active
    response = make_response(expires_in=-1)
    assert response.active_until(0)

    response = make_response(expires_in=10)
    # relative time
    assert response.active_until(5)
    assert not response.active_until(15)
    # absolute time
    now = int(time.time())
    assert response.active_until(now + 5, relative_time=False)
    assert not response.active_until(now + 15, relative_time=False)


def test_always_activated():
    """
    Gets always_activated property from made responses, validates results
    """
    response = make_response(expires_in=-1)
    assert response.always_activated

    response = make_response(expires_in=0)
    assert not response.always_activated
