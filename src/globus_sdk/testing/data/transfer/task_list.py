import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

source_id = str(uuid.uuid4())
destination_id = str(uuid.uuid4())
owner_id = str(uuid.uuid4())
task_id = str(uuid.uuid4())

TASK_LIST_DOC = {
    "DATA": [
        {
            "bytes_checksummed": 0,
            "bytes_transferred": 4,
            "canceled_by_admin": None,
            "canceled_by_admin_message": None,
            "command": "API 0.10",
            "completion_time": "2021-09-02T18:04:49+00:00",
            "deadline": "2021-09-03T18:04:47+00:00",
            "delete_destination_extra": False,
            "destination_endpoint": "mydest",
            "destination_endpoint_display_name": "Destination Endpoint",
            "destination_endpoint_id": destination_id,
            "directories": 0,
            "effective_bytes_per_second": 3,
            "encrypt_data": False,
            "fail_on_quota_errors": False,
            "fatal_error": None,
            "faults": 0,
            "files": 1,
            "files_skipped": 0,
            "files_transferred": 1,
            "filter_rules": None,
            "history_deleted": False,
            "is_ok": None,
            "is_paused": False,
            "label": None,
            "nice_status": None,
            "nice_status_details": None,
            "nice_status_expires_in": None,
            "nice_status_short_description": None,
            "owner_id": owner_id,
            "preserve_timestamp": False,
            "recursive_symlinks": "ignore",
            "request_time": "2021-09-02T18:04:47+00:00",
            "skip_source_errors": False,
            "source_endpoint": "mysrc",
            "source_endpoint_display_name": "Source Endpoint",
            "source_endpoint_id": source_id,
            "status": "SUCCEEDED",
            "subtasks_canceled": 0,
            "subtasks_expired": 0,
            "subtasks_failed": 0,
            "subtasks_pending": 0,
            "subtasks_retrying": 0,
            "subtasks_skipped_errors": 0,
            "subtasks_succeeded": 2,
            "subtasks_total": 2,
            "symlinks": 0,
            "sync_level": None,
            "task_id": task_id,
            "type": "TRANSFER",
            "username": "u_XrtivK6z9w2MZwr65os6nZX0wv",
            "verify_checksum": True,
        }
    ],
    "DATA_TYPE": "task_list",
    "length": 1,
    "limit": 1000,
    "offset": 0,
    "total": 1,
}


RESPONSES = ResponseSet(
    metadata={
        "tasks": [
            {
                "source_id": source_id,
                "destination_id": destination_id,
                "owner_id": owner_id,
                "task_id": task_id,
            }
        ],
    },
    default=RegisteredResponse(
        service="transfer",
        path="/v0.10/task_list",
        json=TASK_LIST_DOC,
    ),
)
