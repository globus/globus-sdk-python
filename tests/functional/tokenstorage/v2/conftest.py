import time
import uuid
from unittest import mock

import pytest

import globus_sdk
from globus_sdk.testing import RegisteredResponse
from globus_sdk.token_storage import TokenStorageData


@pytest.fixture
def id_token_sub():
    return str(uuid.UUID(int=1))


@pytest.fixture
def cc_auth_client():
    client = globus_sdk.ConfidentialAppAuthClient("dummy_id", "dummy_secret")
    with client.retry_config.tune(max_retries=0):
        yield client


@pytest.fixture
def mock_token_data_by_resource_server():
    expiration_time = int(time.time()) + 3600
    ret = {
        "resource_server_1": TokenStorageData(
            resource_server="resource_server_1",
            identity_id="user_id",
            scope="scope1",
            access_token="access_token_1",
            refresh_token="refresh_token_1",
            expires_at_seconds=expiration_time,
            token_type="Bearer",
        ),
        "resource_server_2": TokenStorageData(
            resource_server="resource_server_2",
            identity_id="user_id",
            scope="scope2 scope2:0 scope2:1",
            access_token="access_token_2",
            refresh_token="refresh_token_2",
            expires_at_seconds=expiration_time,
            token_type="Bearer",
        ),
    }
    return ret


@pytest.fixture
def mock_response():
    res = mock.Mock()
    expiration_time = int(time.time()) + 3600
    res.by_resource_server = {
        "resource_server_1": {
            "access_token": "access_token_1",
            "expires_at_seconds": expiration_time,
            "refresh_token": "refresh_token_1",
            "resource_server": "resource_server_1",
            "scope": "scope1",
            "token_type": "Bearer",
        },
        "resource_server_2": {
            "access_token": "access_token_2",
            "expires_at_seconds": expiration_time,
            "refresh_token": "refresh_token_2",
            "resource_server": "resource_server_2",
            "scope": "scope2 scope2:0 scope2:1",
            "token_type": "Bearer",
        },
    }
    res.decode_id_token.return_value = {"sub": "user_id"}

    return res


@pytest.fixture
def dependent_token_response(cc_auth_client):
    expiration_time = int(time.time()) + 3600
    RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        json=[
            {
                "access_token": "access_token_1",
                "expires_at_seconds": expiration_time,
                "refresh_token": "refresh_token_1",
                "resource_server": "resource_server_1",
                "scope": "scope1",
                "token_type": "Bearer",
            },
            {
                "access_token": "access_token_2",
                "expires_at_seconds": expiration_time,
                "refresh_token": "refresh_token_2",
                "resource_server": "resource_server_2",
                "scope": "scope2 scope2:0 scope2:1",
                "token_type": "Bearer",
            },
        ],
    ).add()
    return cc_auth_client.oauth2_get_dependent_tokens("dummy_tok")


@pytest.fixture
def authorization_code_response(cc_auth_client, id_token_sub):
    cc_auth_client.oauth2_start_flow("https://example.com/redirect-uri", "dummy-scope")

    expiration_time = int(time.time()) + 3600
    RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        json={
            "access_token": "access_token_1",
            "expires_at_seconds": expiration_time,
            "refresh_token": "refresh_token_1",
            "resource_server": "resource_server_1",
            "scope": "scope1",
            "token_type": "Bearer",
            "id_token": "dummy_id_token",
            "other_tokens": [
                {
                    "access_token": "access_token_2",
                    "expires_at_seconds": expiration_time,
                    "refresh_token": "refresh_token_2",
                    "resource_server": "resource_server_2",
                    "scope": "scope2 scope2:0 scope2:1",
                    "token_type": "Bearer",
                },
            ],
        },
    ).add()

    # because it's more difficult to mock the full decode_id_token() interaction in
    # detail, directly mock the result of it to return the desired subject (identity_id)
    # value
    response = cc_auth_client.oauth2_exchange_code_for_tokens("dummy_code")
    with mock.patch.object(response, "decode_id_token", lambda: {"sub": id_token_sub}):
        yield response


@pytest.fixture
def refresh_token_response(cc_auth_client):
    expiration_time = int(time.time()) + 3600
    RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        json={
            "access_token": "access_token_1",
            "expires_at_seconds": expiration_time,
            "refresh_token": "refresh_token_1",
            "resource_server": "resource_server_1",
            "scope": "scope1",
            "token_type": "Bearer",
            "other_tokens": [],
        },
    ).add()
    return cc_auth_client.oauth2_refresh_token("dummy_token")
