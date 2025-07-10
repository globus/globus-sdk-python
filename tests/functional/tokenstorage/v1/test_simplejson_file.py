import json
import os

import pytest

from globus_sdk import __version__
from globus_sdk.token_storage import SimpleJSONFileAdapter

IS_WINDOWS = os.name == "nt"


@pytest.fixture
def json_file(tmp_path):
    return tmp_path / "mydata.json"


def test_file_does_not_exist(json_file):
    adapter = SimpleJSONFileAdapter(json_file)
    assert not adapter.file_exists()


def test_file_exists(json_file):
    json_file.touch()
    adapter = SimpleJSONFileAdapter(json_file)
    assert adapter.file_exists()


def test_store(json_file, mock_response):
    adapter = SimpleJSONFileAdapter(json_file)
    assert not adapter.file_exists()
    adapter.store(mock_response)

    data = json.loads(json_file.read_text())
    assert data["globus-sdk.version"] == __version__
    assert data["by_rs"]["resource_server_1"]["access_token"] == "access_token_1"
    assert data["by_rs"]["resource_server_2"]["access_token"] == "access_token_2"


def test_get_token_data(json_file, mock_response):
    adapter = SimpleJSONFileAdapter(json_file)
    assert not adapter.file_exists()
    adapter.store(mock_response)

    data = adapter.get_token_data("resource_server_1")
    assert data["access_token"] == "access_token_1"


def test_store_and_refresh(json_file, mock_response, mock_refresh_response):
    adapter = SimpleJSONFileAdapter(json_file)
    assert not adapter.file_exists()
    adapter.store(mock_response)

    # rs1 and rs2 data was stored correctly
    data = adapter.get_token_data("resource_server_1")
    assert data["access_token"] == "access_token_1"
    data = adapter.get_token_data("resource_server_2")
    assert data["access_token"] == "access_token_2"

    # "refresh" happens, this should change rs2 but not rs1
    adapter.store(mock_refresh_response)
    data = adapter.get_token_data("resource_server_1")
    assert data["access_token"] == "access_token_1"
    data = adapter.get_token_data("resource_server_2")
    assert data["access_token"] == "access_token_2_refreshed"


@pytest.mark.xfail(IS_WINDOWS, reason="cannot set umask perms on Windows")
def test_store_perms(json_file, mock_response):
    adapter = SimpleJSONFileAdapter(json_file)
    assert not adapter.file_exists()
    adapter.store(mock_response)

    # mode|0600 should be 0600 -- meaning that those are the maximal
    # permissions given
    st_mode = json_file.stat().st_mode & 0o777  # & 777 to remove extra bits
    assert st_mode | 0o600 == 0o600
