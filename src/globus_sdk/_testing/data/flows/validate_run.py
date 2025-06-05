from responses import matchers

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
        "request_params": validate_simple_input_request,
    },
    default=RegisteredResponse(
        service="flows",
        path=f"/flows/{TWO_HOP_TRANSFER_FLOW_ID}/validate_run",
        method="POST",
        status=200,
        json=VALIDATE_RUN_SIMPLE_SUCCESS_RESPONSE,
        match=[
            matchers.json_params_matcher(
                params={"body": VALIDATE_RUN_SIMPLE_INPUT_BODY},
                strict_match=False,
            )
        ],
    ),
    invalid_body=RegisteredResponse(
        service="flows",
        path=f"/flows/{TWO_HOP_TRANSFER_FLOW_ID}/validate_run",
        method="POST",
        status=422,
        match=[
            matchers.json_params_matcher(
                params={"body": VALIDATE_RUN_SIMPLE_INPUT_BODY},
                strict_match=False,
            )
        ],
    ),
)
