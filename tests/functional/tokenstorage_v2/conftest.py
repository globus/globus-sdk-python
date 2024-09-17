import time
from unittest import mock

import pytest

from globus_sdk.experimental.tokenstorage import TokenStorageData


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
