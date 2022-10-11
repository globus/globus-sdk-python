from typing import Any, Dict

TWO_HOP_TRANSFER_FLOW_ID = "24bc4997-b483-4c25-a19c-64b0afc00743"
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
    "globus_auth_scope": "https://auth.globus.org/scopes/"
    + TWO_HOP_TRANSFER_FLOW_ID
    + "/flow_24bc4997_b483_4c25_a19c_64b0afc00743_user",
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
    "created_by": "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
    "visible_to": [],
    "runnable_by": [],
    "administered_by": [],
    "action_url": f"https://flows.globus.org/flows/{TWO_HOP_TRANSFER_FLOW_ID}",
    "flow_url": f"https://flows.globus.org/flows/{TWO_HOP_TRANSFER_FLOW_ID}",
    "flow_owner": "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
    "flow_viewers": [
        "public",
        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
    ],
    "flow_starters": [
        "all_authenticated_users",
        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
    ],
    "flow_administrators": [
        "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150"
    ],
}

TWO_HOP_TRANSFER_RUN_ID = "36ad9f9a-ad29-488f-beb4-c22ab729643a"
TWO_HOP_TRANSFER_RUN: Dict[str, Any] = {
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
