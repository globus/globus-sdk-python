from globus_sdk._testing.models import RegisteredResponse, ResponseSet

transfer_data = {
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
            "destination_endpoint": "go#ep2",
            "destination_endpoint_display_name": "Globus Tutorial Endpoint 2",
            "destination_endpoint_id": "ddb59af0-6d04-11e5-ba46-22000b92c6ec",
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
            "source_endpoint": "go#ep1",
            "source_endpoint_display_name": "Globus Tutorial Endpoint 1",
            "source_endpoint_id": "ddb59aef-6d04-11e5-ba46-22000b92c6ec",
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

JOB_ID = "c59d942e-cd54-4711-93dd-4515de55a5f9"
JOB_JSON = {
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
            "source_endpoint_id": "ddb59aef-6d04-11e5-ba46-22000b92c6ec",
            "destination_endpoint_id": "ddb59af0-6d04-11e5-ba46-22000b92c6ec",
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
    "job_id": JOB_ID,
    "status": "loaded",
    "submitted_at": "2022-04-01T19:29:55.942546+00:00",
    "last_ran_at": "2022-04-01T19:30:07.103090+00:00",
    "next_run": "2022-04-11T19:30:00+00:00",
    "n_runs": 1,
    "n_errors": 0,
    "results": {"data": [transfer_data], "page_next": None},
}

JOB_JSON_INACTIVE_USER = {
    **JOB_JSON,
    "status": "inactive",
    "inactive_reason": {"cause": "user", "detail": None},
}

JOB_JSON_INACTIVE_GARE = {
    **JOB_JSON,
    "status": "inactive",
    "inactive_reason": {
        "cause": "globus_auth_requirements",
        "detail": {
            "code": "ConsentRequired",
            "authorization_parameters": {
                "session_message": "Missing required data_access consent",
                "required_scopes": [
                    (
                        "https://auth.globus.org/scopes/actions.globus.org/"
                        "transfer/transfer"
                        "[urn:globus:auth:scope:transfer.api.globus.org:all"
                        "[*https://auth.globus.org/scopes/"
                        "543aade1-db97-4a4b-9bdf-0b58e78dfa69/data_access]]"
                    )
                ],
            },
        },
    },
}


RESPONSES = ResponseSet(
    metadata={"job_id": JOB_ID},
    default=RegisteredResponse(
        service="timer",
        path=f"/jobs/{JOB_ID}",
        method="GET",
        json=JOB_JSON,
    ),
    inactive_gare=RegisteredResponse(
        service="timer",
        path=f"/jobs/{JOB_ID}",
        method="GET",
        json=JOB_JSON_INACTIVE_GARE,
    ),
    inactive_user=RegisteredResponse(
        service="timer",
        path=f"/jobs/{JOB_ID}",
        method="GET",
        json=JOB_JSON_INACTIVE_USER,
    ),
    simple_500_error=RegisteredResponse(
        service="timer",
        path=f"/jobs/{JOB_ID}",
        method="GET",
        status=500,
        json={
            "error": {
                "code": "ERROR",
                "detail": "Request failed terribly",
                "status": 500,
            }
        },
    ),
)
