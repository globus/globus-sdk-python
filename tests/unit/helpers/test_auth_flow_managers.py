import base64
import hashlib
import os
from unittest import mock

import pytest

import globus_sdk
from globus_sdk.scopes import TransferScopes
from globus_sdk.services.auth.flow_managers.authorization_code import (
    GlobusAuthorizationCodeFlowManager,
)
from globus_sdk.services.auth.flow_managers.native_app import _make_native_app_challenge


@pytest.mark.parametrize(
    "verifier",
    [
        "x" * 20,  # too short
        "x" * 200,  # too long
        ("x" * 40) + "/" + ("y" * 40),  # includes invalid characters
    ],
)
def test_invalid_native_app_challenge(verifier):
    with pytest.raises(globus_sdk.GlobusSDKUsageError):
        _make_native_app_challenge(verifier)


def test_simple_input_native_app_challenge():
    verifier = "x" * 80
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest())
        .rstrip(b"=")
        .decode("utf-8")
    )
    res_verifier, res_challenge = _make_native_app_challenge(verifier)
    assert res_verifier == verifier
    assert res_challenge == challenge


def test_random_native_app_challenge(monkeypatch):
    b64vals = []

    def mock_urandom(n: int):
        return b"xyz"

    def mock_b64encode(b: bytes):
        b64vals.append(b)
        return b"abc123"

    monkeypatch.setattr(os, "urandom", mock_urandom)
    monkeypatch.setattr(base64, "urlsafe_b64encode", mock_b64encode)

    verifier, challenge = _make_native_app_challenge()
    assert verifier == "abc123"
    assert challenge == "abc123"

    assert len(b64vals) == 2
    assert b64vals == [b"xyz", hashlib.sha256(b"abc123").digest()]


def test_get_authorize_url_for_authorization_code():
    mock_client = mock.Mock()
    mock_client.client_id = "MOCK_CLIENT_ID"
    mock_client.base_url = "https://auth.globus.org/"
    flow_manager = GlobusAuthorizationCodeFlowManager(
        mock_client,
        redirect_uri="https://foo.example.org/authenticate",
        requested_scopes=TransferScopes.all,
    )

    silly_string = "ANANAS_IS_PINEAPPLE_BUT_BANANE_IS_BANANA"

    authorize_url = flow_manager.get_authorize_url()
    assert authorize_url.startswith("https://auth.globus.org")
    assert silly_string not in authorize_url

    silly_authorize_url = flow_manager.get_authorize_url(
        query_params={"silly_string": silly_string}
    )
    assert silly_string in silly_authorize_url
