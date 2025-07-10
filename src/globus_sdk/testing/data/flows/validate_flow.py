from responses import matchers

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

VALIDATE_SIMPLE_FLOW_DEFINITION = {
    "Comment": "Simple flow",
    "StartAt": "Step1",
    "States": {
        "Step1": {
            "Type": "Action",
            "ActionUrl": "https://transfer.actions.globus.org/transfer",
            "Parameters": {
                "source_endpoint.$": "$.source_endpoint_id",
                "destination_endpoint.$": "$.destination_endpoint_id",
                "DATA": [
                    {
                        "source_path.$": "$.source_path",
                        "destination_path.$": "$.destination_path",
                    }
                ],
            },
            "ResultPath": "$.TransferResult",
            "End": True,
        }
    },
}

VALIDATE_SIMPLE_SUCCESS_RESPONSE = {
    "scopes": {"User": ["urn:globus:auth:scope:transfer.api.globus.org:all"]}
}

VALIDATE_INVALID_FLOW_DEFINITION = {
    "Comment": "Simple flow",
    "StartAt": "Step1",
    "States": {
        "Step1": {
            "Type": "Action",
            "ActionUrl": "https://transfer.actions.globus.org/transfer",
            "Parameters": {
                "source_endpoint.$": "$.source_endpoint_id",
                "destination_endpoint.$": "$.destination_endpoint_id",
                "DATA": [
                    {
                        "source_path.$": "$.source_path",
                        "destination_path.$": "$.destination_path",
                    }
                ],
            },
            "ResultPath": "$.TransferResult",
        }
    },
}

VALIDATE_INVALID_RESPONSE = {
    "error": {
        "code": "UNPROCESSABLE_ENTITY",
        "detail": [
            {
                "loc": ["definition", "States", "Step1"],
                "msg": (
                    "A state of type 'Action' must be defined as either terminal "
                    '("End": true) or transitional ("Next": "NextStateId")'
                ),
                "type": "value_error",
            }
        ],
        "message": (
            "1 validation error in body. $.definition.States.Step1: A state of "
            "type 'Action' must be defined as either terminal (\"End\": true) "
            'or transitional ("Next": "NextStateId")'
        ),
    },
    "debug_id": "41267e70-6788-4316-8b67-df7160166466",
}

_validate_simple_flow_request = {
    "definition": VALIDATE_SIMPLE_FLOW_DEFINITION,
}

_validate_invalid_flow_request = {
    "definition": VALIDATE_INVALID_FLOW_DEFINITION,
}

RESPONSES = ResponseSet(
    metadata={
        "success": VALIDATE_SIMPLE_FLOW_DEFINITION,
        "invalid": VALIDATE_INVALID_FLOW_DEFINITION,
    },
    default=RegisteredResponse(
        service="flows",
        path="/flows/validate",
        method="POST",
        status=200,
        json=VALIDATE_SIMPLE_SUCCESS_RESPONSE,
        match=[
            matchers.json_params_matcher(
                params={"definition": VALIDATE_SIMPLE_FLOW_DEFINITION},
                strict_match=False,
            )
        ],
    ),
    definition_error=RegisteredResponse(
        service="flows",
        path="/flows/validate",
        method="POST",
        status=422,
        json=VALIDATE_INVALID_RESPONSE,
        match=[
            matchers.json_params_matcher(
                params={"definition": VALIDATE_INVALID_FLOW_DEFINITION},
                strict_match=False,
            )
        ],
    ),
)
