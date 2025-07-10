import uuid

TIMER_ID = str(uuid.uuid1())

DEST_EP_ID = str(uuid.uuid1())
SOURCE_EP_ID = str(uuid.uuid1())


V2_TRANSFER_TIMER = {
    "body": {
        "DATA": [
            {
                "DATA_TYPE": "transfer_item",
                "destination_path": "/~/dst.txt",
                "source_path": "/share/godata/file1.txt",
            }
        ],
        "DATA_TYPE": "transfer",
        "delete_destination_extra": False,
        "destination_endpoint": DEST_EP_ID,
        "encrypt_data": False,
        "fail_on_quota_errors": False,
        "notify_on_failed": True,
        "notify_on_inactive": True,
        "notify_on_succeeded": True,
        "preserve_timestamp": False,
        "skip_source_errors": False,
        "source_endpoint": SOURCE_EP_ID,
        "store_base_path_info": False,
        "verify_checksum": True,
    },
    "inactive_reason": None,
    "job_id": TIMER_ID,
    "last_ran_at": None,
    "name": "Very Cool Timer",
    "next_run": "2023-10-27T05:00:00+00:00",
    "number_of_errors": 0,
    "number_of_runs": 0,
    "schedule": {
        "type": "recurring",
        "end": {"count": 2},
        "interval_seconds": 604800,
        "start": "2023-10-27T05:00:00+00:00",
    },
    "status": "new",
    "submitted_at": "2023-10-26T20:31:09+00:00",
}


# V1 API data

_transfer_data = {
    "data": {
        "action_id": "15jfdBESgveZQ",
        "completion_time": "2022-04-01T19:30:05.973261+00:00",
        "creator_id": "urn:globus:auth:identity:5276fa05-eedf-46c5-919f-ad2d0160d1a9",
        "details": {
            "DATA_TYPE": "task",
            "bytes_checksummed": 0,
            "bytes_transferred": 0,
            "canceled_by_admin": None,
            "canceled_by_admin_message": None,
            "command": "API 0.10",
            "completion_time": None,
            "deadline": "2022-04-02T19:30:07+00:00",
            "delete_destination_extra": False,
            "destination_endpoint": "globus#dest_ep",
            "destination_endpoint_display_name": "Some Dest Endpoint",
            "destination_endpoint_id": DEST_EP_ID,
            "directories": 0,
            "effective_bytes_per_second": 0,
            "encrypt_data": False,
            "event_list": [],
            "fail_on_quota_errors": False,
            "fatal_error": None,
            "faults": 0,
            "files": 0,
            "files_skipped": 0,
            "files_transferred": 0,
            "filter_rules": None,
            "history_deleted": False,
            "is_ok": True,
            "is_paused": False,
            "label": "example timer, run 1",
            "nice_status": "Queued",
            "nice_status_details": None,
            "nice_status_expires_in": -1,
            "nice_status_short_description": "Queued",
            "owner_id": "5276fa05-eedf-46c5-919f-ad2d0160d1a9",
            "preserve_timestamp": False,
            "recursive_symlinks": "ignore",
            "request_time": "2022-04-01T19:30:07+00:00",
            "skip_source_errors": True,
            "source_endpoint": "globus#src_ep",
            "source_endpoint_display_name": "Some Source Endpoint",
            "source_endpoint_id": SOURCE_EP_ID,
            "status": "ACTIVE",
            "subtasks_canceled": 0,
            "subtasks_expired": 0,
            "subtasks_failed": 0,
            "subtasks_pending": 1,
            "subtasks_retrying": 0,
            "subtasks_skipped_errors": 0,
            "subtasks_succeeded": 0,
            "subtasks_total": 1,
            "symlinks": 0,
            "sync_level": 3,
            "task_id": "22f0148c-b1f2-11ec-b87e-3912f602f346",
            "type": "TRANSFER",
            "username": "u_kj3pubpo35dmlem7vuwqcygrve",
            "verify_checksum": True,
        },
        "display_status": "ACTIVE",
        "label": None,
        "manage_by": [],
        "monitor_by": [],
        "release_after": "P30D",
        "start_time": "2022-04-01T19:30:05.973232+00:00",
        "status": "ACTIVE",
    },
    "errors": None,
    "status": 202,
    "ran_at": "2022-04-01T19:30:07.103090",
}
V1_TIMER = {
    "name": "example timer",
    "start": "2022-04-01T19:30:00+00:00",
    "stop_after": None,
    "interval": 864000.0,
    "callback_url": "https://actions.automate.globus.org/transfer/transfer/run",
    "callback_body": {
        "body": {
            "label": "example timer",
            "skip_source_errors": True,
            "sync_level": 3,
            "verify_checksum": True,
            "source_endpoint_id": "aa752cea-8222-5bc8-acd9-555b090c0ccb",
            "destination_endpoint_id": "313ce13e-b597-5858-ae13-29e46fea26e6",
            "transfer_items": [
                {
                    "source_path": "/share/godata/file1.txt",
                    "destination_path": "/~/file1.txt",
                    "recursive": False,
                }
            ],
        }
    },
    "inactive_reason": None,
    "scope": None,
    "job_id": TIMER_ID,
    "status": "loaded",
    "submitted_at": "2022-04-01T19:29:55.942546+00:00",
    "last_ran_at": "2022-04-01T19:30:07.103090+00:00",
    "next_run": "2022-04-11T19:30:00+00:00",
    "n_runs": 1,
    "n_errors": 0,
    "results": {"data": [_transfer_data], "page_next": None},
}
