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
    "keywords": [],
    "principal_urn": f"urn:globus:auth:identity:{TWO_HOP_TRANSFER_FLOW_ID}",
    "globus_auth_username": (f"{TWO_HOP_TRANSFER_FLOW_ID}@clients.auth.globus.org"),
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
    "flow_viewers": [],
    "flow_starters": [],
    "flow_administrators": [],
}
