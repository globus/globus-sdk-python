import time
from unittest import mock

from globus_sdk.token_storage.v1 import MemoryAdapter


def test_memory_adapter_store_overwrites_only_new_data():
    # setup a mock token response
    expiration_time = int(time.time()) + 3600
    mock_response = mock.Mock()
    mock_response.by_resource_server = {
        "resource_server_1": {
            "access_token": "access_token_1",
            "expires_at_seconds": expiration_time,
            "refresh_token": "refresh_token_1",
            "resource_server": "resource_server_1",
            "scope": "scope1",
            "token_type": "bearer",
        },
        "resource_server_2": {
            "access_token": "access_token_2",
            "expires_in": expiration_time,
            "refresh_token": "refresh_token_2",
            "resource_server": "resource_server_2",
            "scope": "scope2 scope2:0 scope2:1",
            "token_type": "bearer",
        },
    }

    # "store" it in memory
    adapter = MemoryAdapter()
    adapter.store(mock_response)

    # read back a sample piece of data
    fetch1 = adapter.get_token_data("resource_server_1")
    assert fetch1["access_token"] == "access_token_1"

    # "store" a new mock response which overwrites only one piece of data
    mock_response2 = mock.Mock()
    mock_response2.by_resource_server = {
        "resource_server_1": {
            "access_token": "access_token_1_new",
            "expires_at_seconds": expiration_time,
            "refresh_token": "refresh_token_1",
            "resource_server": "resource_server_1",
            "scope": "scope1",
            "token_type": "bearer",
        }
    }
    adapter.store(mock_response2)

    # the overwritten data is updated
    fetch2 = adapter.get_token_data("resource_server_1")
    assert fetch2["access_token"] == "access_token_1_new"

    # but the existing data is preserved
    fetch3 = adapter.get_token_data("resource_server_2")
    assert fetch3["access_token"] == "access_token_2"
