import json
import os

import pytest

from globus_sdk.tokenstorage import JSONTokenStorage, SimpleJSONFileAdapter
from globus_sdk.version import __version__

IS_WINDOWS = os.name == "nt"


@pytest.fixture
def json_file(tmp_path):
    return tmp_path / "mydata.json"


def test_file_does_not_exist(json_file):
    adapter = JSONTokenStorage(json_file)
    assert not adapter.file_exists()


def test_file_exists(json_file):
    json_file.touch()
    adapter = JSONTokenStorage(json_file)
    assert adapter.file_exists()


def test_store_and_get_token_data_by_resource_server(
    json_file, mock_token_data_by_resource_server
):
    adapter = JSONTokenStorage(json_file)
    assert not adapter.file_exists()
    adapter.store_token_data_by_resource_server(mock_token_data_by_resource_server)

    gotten = adapter.get_token_data_by_resource_server()

    for resource_server in ["resource_server_1", "resource_server_2"]:
        assert (
            mock_token_data_by_resource_server[resource_server].to_dict()
            == gotten[resource_server].to_dict()
        )


def test_store_token_response_with_namespace(json_file, mock_response):
    adapter = JSONTokenStorage(json_file, namespace="foo")
    assert not adapter.file_exists()
    adapter.store_token_response(mock_response)

    data = json.loads(json_file.read_text())
    assert data["globus-sdk.version"] == __version__
    assert data["data"]["foo"]["resource_server_1"]["access_token"] == "access_token_1"
    assert data["data"]["foo"]["resource_server_2"]["access_token"] == "access_token_2"


def test_get_token_data(json_file, mock_response):
    adapter = JSONTokenStorage(json_file)
    assert not adapter.file_exists()
    adapter.store_token_response(mock_response)

    assert adapter.get_token_data("resource_server_1").access_token == "access_token_1"


def test_remove_token_data(json_file, mock_response):
    adapter = JSONTokenStorage(json_file)
    assert not adapter.file_exists()
    adapter.store_token_response(mock_response)

    # remove rs1, confirm only rs2 is still available
    remove_result = adapter.remove_token_data("resource_server_1")
    assert remove_result is True

    assert adapter.get_token_data("resource_server_1") is None
    assert adapter.get_token_data("resource_server_2").access_token == "access_token_2"

    # confirm unable to re-remove rs1
    remove_result = adapter.remove_token_data("resource_server_1")
    assert remove_result is False


@pytest.mark.xfail(IS_WINDOWS, reason="cannot set umask perms on Windows")
def test_store_perms(json_file, mock_response):
    adapter = JSONTokenStorage(json_file)
    assert not adapter.file_exists()
    adapter.store_token_response(mock_response)

    # mode|0600 should be 0600 -- meaning that those are the maximal
    # permissions given
    st_mode = json_file.stat().st_mode & 0o777  # & 777 to remove extra bits
    assert st_mode | 0o600 == 0o600


def test_migrate_from_v1_adapter(json_file, mock_response):
    # write with a SimpleJSONFileAdapter
    old_adapter = SimpleJSONFileAdapter(json_file)
    old_adapter.store(mock_response)

    # confirm able to read with JSONTokenStorage
    new_adapter = JSONTokenStorage(json_file)
    assert (
        new_adapter.get_token_data("resource_server_1").access_token == "access_token_1"
    )

    # confirm version is overwritten on next store
    new_adapter.store_token_response(mock_response)
    data = json.loads(json_file.read_text())
    assert data["format_version"] == "2.0"
