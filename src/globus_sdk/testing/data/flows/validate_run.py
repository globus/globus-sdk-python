from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_FLOW_ID

VALIDATE_RUN_SIMPLE_INPUT_BODY = {"param": "value"}

VALIDATE_INVALID_SIMPLE_INPUT_BODY = {"foo": "bar"}

VALIDATE_RUN_SIMPLE_SUCCESS_RESPONSE = {"message": "validation successful"}

validate_simple_input_request = {
    "body": VALIDATE_RUN_SIMPLE_INPUT_BODY,
}

validate_invalid_simple_input_request = {
    "body": VALIDATE_INVALID_SIMPLE_INPUT_BODY,
}


RESPONSES = ResponseSet(
    metadata={
        "flow_id": TWO_HOP_TRANSFER_FLOW_ID,
        "request_body": VALIDATE_RUN_SIMPLE_INPUT_BODY,
    },
    default=RegisteredResponse(
        service="flows",
        path=f"/flows/{TWO_HOP_TRANSFER_FLOW_ID}/validate_run",
        method="POST",
        status=200,
        json=VALIDATE_RUN_SIMPLE_SUCCESS_RESPONSE,
    ),
    invalid_input_payload=RegisteredResponse(
        service="flows",
        path=f"/flows/{TWO_HOP_TRANSFER_FLOW_ID}/validate_run",
        method="POST",
        status=400,
        json={
            "error": {
                "code": "FLOW_INPUT_ERROR",
                "detail": [
                    {
                        "loc": ["$.bool"],
                        "type": "InvalidActionInput",
                        "msg": "'not-a-boolean' is not of type 'boolean'",
                    }
                ],
                "message": "Input failed schema validation with 1 error.",
            },
            "debug_id": "00000000-2572-411b-9fa9-c72fbed2b0bb",
        },
    ),
    invalid_token=RegisteredResponse(
        service="flows",
        path=f"/flows/{TWO_HOP_TRANSFER_FLOW_ID}/validate_run",
        method="POST",
        status=401,
        json={
            "error": {
                "code": "AUTHENTICATION_ERROR",
                "detail": "Expired or invalid Bearer token",
            },
            "debug_id": "00000000-1ca9-477d-9937-a26c9d9384b9",
        },
    ),
    not_a_flow_starter=RegisteredResponse(
        service="flows",
        path=f"/flows/{TWO_HOP_TRANSFER_FLOW_ID}/validate_run",
        method="POST",
        status=403,
        json={
            "error": {
                "code": "FORBIDDEN",
                "detail": (
                    "You do not have the necessary permissions to perform this action"
                    " on the flow with id value 00000000-0a9d-4036-a9d7-a77c19515594."
                    " Missing permissions: RUN."
                ),
            },
            "debug_id": "00000000-16c3-4872-8bb5-47db18227cb0",
        },
    ),
)
