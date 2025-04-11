from __future__ import annotations

import typing as t
import uuid

TWO_HOP_TRANSFER_FLOW_ID = "24bc4997-b483-4c25-a19c-64b0afc00743"
TWO_HOP_TRANSFER_FLOW_OWNER_ID = "b44bddda-d274-11e5-978a-9f15789a8150"

FLOW_ID = str(uuid.uuid1())
RUN_ID = str(uuid.uuid1())
USER1 = f"urn:globus:auth:identity:{uuid.uuid1()}"
USER2 = f"urn:globus:auth:identity:{uuid.uuid1()}"
GROUP = f"urn:globus:groups:id:{uuid.uuid1()}"
RUN_MANAGER_PRINCIPAL = f"urn:globus:auth:identity:{str(uuid.uuid1())}"
RUN_MONITOR_PRINCIPAL = f"urn:globus:auth:identity:{str(uuid.uuid1())}"

TWO_HOP_TRANSFER_FLOW_USER_SCOPE = (
    "https://auth.globus.org/scopes/"
    + TWO_HOP_TRANSFER_FLOW_ID
    + "/flow_"
    + TWO_HOP_TRANSFER_FLOW_ID.replace("-", "_")
    + "_user"
)

TWO_HOP_TRANSFER_FLOW_DEFINITION = {
    "States": {
        "Transfer1": {
            "Next": "Transfer2",
            "Type": "Action",
            "Comment": "Initial Transfer from Campus to DMZ",
            "ActionUrl": "https://actions.globus.org/transfer/transfer",
            "Parameters": {
                "transfer_items": [
                    {
                        "recursive": True,
                        "source_path.$": "$.source_path",
                        "destination_path.$": "$.staging_path",
                    }
                ],
                "source_endpoint_id.$": "$.source_endpoint_id",
                "destination_endpoint_id.$": "$.staging_endpoint_id",
            },
            "ResultPath": "$.Transfer1Result",
            "ActionScope": (
                "https://auth.globus.org/scopes/actions.globus.org/transfer/transfer"
            ),
        },
        "Transfer2": {
            "End": True,
            "Type": "Action",
            "Comment": "Transfer from DMZ to dataset repository",
            "ActionUrl": "https://actions.globus.org/transfer/transfer",
            "Parameters": {
                "transfer_items": [
                    {
                        "recursive": True,
                        "source_path.$": "$.staging_path",
                        "destination_path.$": "$.destination_path",
                    }
                ],
                "source_endpoint_id.$": "$.staging_endpoint_id",
                "destination_endpoint_id.$": "$.destination_endpoint_id",
            },
            "ResultPath": "$.Transfer2Result",
            "ActionScope": (
                "https://auth.globus.org/scopes/actions.globus.org/transfer/transfer"
            ),
        },
    },
    "Comment": "Two step transfer",
    "StartAt": "Transfer1",
}
TWO_HOP_TRANSFER_FLOW_DOC = {
    "id": TWO_HOP_TRANSFER_FLOW_ID,
    "definition": TWO_HOP_TRANSFER_FLOW_DEFINITION,
    "input_schema": {
        "type": "object",
        "required": [
            "source_endpoint_id",
            "source_path",
            "staging_endpoint_id",
            "staging_path",
            "destination_endpoint_id",
            "destination_path",
        ],
        "properties": {
            "source_path": {"type": "string"},
            "staging_path": {"type": "string"},
            "destination_path": {"type": "string"},
            "source_endpoint_id": {"type": "string"},
            "staging_endpoint_id": {"type": "string"},
            "destination_endpoint_id": {"type": "string"},
        },
        "additionalProperties": False,
    },
    "globus_auth_scope": TWO_HOP_TRANSFER_FLOW_USER_SCOPE,
    "synchronous": False,
    "log_supported": True,
    "types": ["Action"],
    "api_version": "1.0",
    "title": "Multi Step Transfer",
    "subtitle": "",
    "description": "",
    "keywords": ["two", "hop", "transfer"],
    "principal_urn": f"urn:globus:auth:identity:{TWO_HOP_TRANSFER_FLOW_ID}",
    "globus_auth_username": f"{TWO_HOP_TRANSFER_FLOW_ID}@clients.auth.globus.org",
    "created_at": "2020-09-01T17:59:20.711845+00:00",
    "updated_at": "2020-09-01T17:59:20.711845+00:00",
    "user_role": "flow_starter",
    "created_by": f"urn:globus:auth:identity:{TWO_HOP_TRANSFER_FLOW_OWNER_ID}",
    "visible_to": [],
    "runnable_by": [],
    "administered_by": [],
    "action_url": f"https://flows.globus.org/flows/{TWO_HOP_TRANSFER_FLOW_ID}",
    "flow_url": f"https://flows.globus.org/flows/{TWO_HOP_TRANSFER_FLOW_ID}",
    "flow_owner": f"urn:globus:auth:identity:{TWO_HOP_TRANSFER_FLOW_OWNER_ID}",
    "flow_viewers": [
        "public",
        "urn:globus:auth:identity:51abb9ce-6e05-4ab1-9a09-9c524313827c",
    ],
    "flow_starters": [
        "all_authenticated_users",
        "urn:globus:auth:identity:d0a15d1b-28f5-42de-9463-b8b6540421b6",
    ],
    "flow_administrators": [
        "urn:globus:auth:identity:05d29dab-bd26-4510-9290-468972e8ac01"
    ],
    "run_managers": [RUN_MANAGER_PRINCIPAL],
    "run_monitors": [RUN_MONITOR_PRINCIPAL],
}

TWO_HOP_TRANSFER_RUN_ID = "36ad9f9a-ad29-488f-beb4-c22ab729643a"
TWO_HOP_TRANSFER_RUN: dict[str, t.Any] = {
    "run_id": TWO_HOP_TRANSFER_RUN_ID,
    "flow_id": TWO_HOP_TRANSFER_FLOW_ID,
    "flow_title": TWO_HOP_TRANSFER_FLOW_DOC["title"],
    "flow_last_updated": "2020-09-01T17:59:20.711845+00:00",
    "start_time": "2020-09-12T15:00:20.711845+00:00",
    "status": "ACTIVE",
    "display_status": "ACTIVE",
    "details": {
        "code": "FlowStarting",
        "description": "The Flow is starting execution",
        "details": {
            "input": {
                "source_endpoint_id": "7e1b8ec7-a606-4c23-96c7-a2d930a3a55f",
                "source_path": "/path/to/the/source/dir",
                "staging_endpoint_id": "d5049dd6-ce9c-4f9e-853f-c25069f369f8",
                "staging_path": "/path/to/the/staging/dir",
                "destination_endpoint_id": "f3bd0daf-be5a-4df8-b53f-76b932113b7c",
                "destination_path": "/path/to/the/dest/dir",
            }
        },
    },
    "run_owner": TWO_HOP_TRANSFER_FLOW_DOC["flow_owner"],
    "run_managers": ["urn:globus:auth:identity:7d6064ef-5368-473a-b15b-e99c3561aa9b"],
    "run_monitors": [
        "urn:globus:auth:identity:58cf49f4-06ea-4b76-934c-d5c9f6c3ea9d",
        "urn:globus:auth:identity:57088a17-d5cb-4cfa-871a-c5cce48f2aec",
    ],
    "user_role": "run_owner",
    "label": "Transfer all of these files!",
    "tags": [
        "my-transfer-run",
        "jazz-fans",
    ],
    "search": {"task_id": "20ba91a8-eb90-470a-9477-2ad68808b276"},
}

FLOW_SCOPE_SUFFIX = f'flow_{FLOW_ID.replace("-", "_")}_user'
FLOW_SCOPE = f"https://auth.globus.org/scopes/{FLOW_ID}/{FLOW_SCOPE_SUFFIX}"
FLOW_DESCRIPTION = {
    "created_at": "2023-04-11T20:00:06.524930+00:00",
    "flow_owner": USER1,
    "created_by": USER1,
    "description": "This flow does some pretty cool stuff",
    "globus_auth_scope": FLOW_SCOPE,
    "id": FLOW_ID,
    "keywords": ["cool"],
    "subtitle": "My Cool Subtitle",
    "title": "My Cool Flow",
    "updated_at": "2023-04-11T20:00:06.524930+00:00",
}
RUN_DETAILS = {
    "code": "FlowSucceeded",
    "description": "The Flow run reached a successful completion state",
    "output": {
        "HelloResult": {
            "action_id": "6RxDm1JOQnG2",
            "completion_time": "2023-04-11T20:01:22.340594+00:00",
            "creator_id": USER1,
            "details": {"Hello": "World", "hello": "foo"},
            "display_status": "SUCCEEDED",
            "label": "My Cool Run",
            "manage_by": [USER2],
            "monitor_by": [GROUP],
            "release_after": None,
            "start_time": "2023-04-11T20:01:19.660251+00:00",
            "state_name": "RunHelloWorld",
            "status": "SUCCEEDED",
        },
        "input": {"echo_string": "foo", "sleep": 2},
    },
}
RUN = {
    "run_id": RUN_ID,
    "action_id": RUN_ID,
    "completion_time": "2023-04-11T20:01:22.917000+00:00",
    "created_by": USER1,
    "details": RUN_DETAILS,
    "display_status": "SUCCEEDED",
    "flow_id": FLOW_ID,
    "flow_last_updated": "2023-04-11T20:00:06.524930+00:00",
    "flow_title": "My Cool Flow",
    "label": "My Cool Run",
    "manage_by": [USER2],
    "monitor_by": [GROUP],
    "run_managers": [USER2],
    "run_monitors": [GROUP],
    "run_owner": USER1,
    "start_time": "2023-04-11T20:01:18.040416+00:00",
    "status": "SUCCEEDED",
    "tags": ["cool", "my"],
    "user_role": "run_owner",
}
