"""
Invariants which hold for every file-based token storage, legacy and current.

The process umask is shared by every thread, so changing it, even temporarily,
can change the permissions of files which other threads are creating.
File-based storages must therefore never leave the umask changed, which they could
do if two writes overlapped and each tried to restore a different "original" umask.
"""

import os
import time
from unittest import mock

import pytest

from globus_sdk.token_storage import JSONTokenStorage, SQLiteTokenStorage
from globus_sdk.token_storage.legacy import SimpleJSONFileAdapter, SQLiteAdapter
from tests.common.overlapping_writes import (
    CheckpointDict,
    OverlappingWrites,
    current_umask,
    process_umask,
    sqlite_factory_with_checkpoint,
)

IS_WINDOWS = os.name == "nt"


@pytest.fixture(
    params=[SQLiteAdapter, SQLiteTokenStorage, JSONTokenStorage, SimpleJSONFileAdapter]
)
def overlapping_file_writes(request, tmp_path):
    """
    Return a function which runs two writes, to two different files, so that they
    overlap in the order described by ``OverlappingWrites``.

    For each storage class, "a write" must call the checkpoint
    while the class is in the middle of creating its file.
    How that is arranged depends on how the class writes its file.
    """
    cls = request.param
    mock_token_data = {
        "access_token": "access_token_1",
        "expires_at_seconds": int(time.time()) + 3600,
        "refresh_token": "refresh_token_1",
        "resource_server": "resource_server_1",
        "scope": "scope1",
        "token_type": "bearer",
    }

    if cls in (SQLiteAdapter, SQLiteTokenStorage):

        def write_file(filename_stem, checkpoint):
            # The checkpoint is called by the `factory` just before the database
            # file is opened (and therefore created).
            obj = cls(
                tmp_path / f"{filename_stem}.db",
                connect_params={
                    "factory": sqlite_factory_with_checkpoint(checkpoint),
                    # adapters are created in worker threads but closed in teardown
                    "check_same_thread": False,
                },
            )
            request.addfinalizer(obj.close)

    elif cls is JSONTokenStorage:

        def write_file(filename_stem, checkpoint):
            # The checkpoint is called when `json.dump()` iterates the token data,
            # which is after the file has been opened.
            slow_token_data = mock.Mock(
                to_dict=lambda: CheckpointDict(checkpoint, mock_token_data)
            )
            cls(tmp_path / f"{filename_stem}.json").store_token_data_by_resource_server(
                {"resource_server_1": slow_token_data}
            )

    elif cls is SimpleJSONFileAdapter:

        def write_file(filename_stem, checkpoint):
            # As above: the checkpoint is called when `json.dump()` iterates
            # the token data, which is after the file has been opened.
            response = mock.Mock()
            response.by_resource_server = {
                "resource_server_1": CheckpointDict(checkpoint, mock_token_data)
            }
            cls(tmp_path / f"{filename_stem}.json").store(response)

    else:
        raise NotImplementedError(cls)

    def run():
        overlap_controller = OverlappingWrites()
        overlap_controller.run(
            lambda: write_file("first", overlap_controller.first_checkpoint),
            lambda: write_file("second", overlap_controller.second_checkpoint),
        )

    return run


@pytest.mark.xfail(IS_WINDOWS, reason="cannot set umask perms on Windows")
def test_overlapping_writes_leave_the_process_umask_alone(overlapping_file_writes):
    with process_umask(0o022):
        overlapping_file_writes()
        assert current_umask() == 0o022
