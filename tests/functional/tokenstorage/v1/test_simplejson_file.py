import os
import stat

import pytest

from globus_sdk import __version__, exc
from globus_sdk.token_storage.legacy import SimpleJSONFileAdapter
from tests.common import fast_json
from tests.common.overlapping_writes import current_umask, process_umask

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

    data = fast_json.loads(json_file.read_text())
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

    assert stat.S_IMODE(json_file.stat().st_mode) == 0o600


@pytest.mark.xfail(IS_WINDOWS, reason="cannot set umask perms on Windows")
def test_user_only_umask_is_deprecated_but_still_works(json_file):
    adapter = SimpleJSONFileAdapter(json_file)
    with process_umask(0o022):
        with pytest.warns(exc.RemovedInV5Warning, match="user_only_umask") as record:
            with adapter.user_only_umask():
                assert current_umask() == 0o177
        assert current_umask() == 0o022
    # the warning points at the caller, not at the SDK or at contextlib
    assert record[0].filename == __file__


@pytest.mark.xfail(IS_WINDOWS, reason="cannot set umask perms on Windows")
def test_store_perms_with_a_umask_that_denies_the_owner(json_file, mock_response):
    adapter = SimpleJSONFileAdapter(json_file)
    with process_umask(0o277):
        adapter.store(mock_response)
        # the owner can still write to the file
        adapter.store(mock_response)
    assert stat.S_IMODE(json_file.stat().st_mode) == 0o600


@pytest.mark.xfail(IS_WINDOWS, reason="cannot set umask perms on Windows")
def test_store_does_not_change_the_perms_of_an_existing_file(json_file, mock_response):
    adapter = SimpleJSONFileAdapter(json_file)
    adapter.store(mock_response)
    json_file.chmod(0o640)
    adapter.store(mock_response)
    assert stat.S_IMODE(json_file.stat().st_mode) == 0o640


def test_owner_only_opener_in_append_mode_keeps_existing_data(json_file):
    for data in ("one", "two"):
        with open(json_file, "a", opener=SimpleJSONFileAdapter._owner_only_opener) as f:
            f.write(data)
    assert json_file.read_text() == "onetwo"


@pytest.mark.xfail(IS_WINDOWS, reason="cannot set umask perms on Windows")
@pytest.mark.parametrize("fchmod_is", ("missing", "failing"))
def test_owner_only_opener_works_when_fchmod_is_unavailable(
    json_file, monkeypatch, fchmod_is
):
    # Windows (before Python 3.13) has no `os.fchmod`,
    # and some filesystems do not support changing modes
    if fchmod_is == "missing":
        monkeypatch.delattr(os, "fchmod")
    else:

        def fchmod(fd, mode):
            raise OSError("chmod is not supported")

        monkeypatch.setattr(os, "fchmod", fchmod)

    with process_umask(0o022):
        with open(json_file, "w", opener=SimpleJSONFileAdapter._owner_only_opener) as f:
            f.write("data")
    assert stat.S_IMODE(json_file.stat().st_mode) == 0o600
    assert json_file.read_text() == "data"
