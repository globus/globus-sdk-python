from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import FUNCTION_CODE, FUNCTION_ID, FUNCTION_NAME

DEFAULT_RESPONSE_DOC = {
    "function_uuid": FUNCTION_ID,
}

RESPONSES = ResponseSet(
    metadata={
        "function_id": FUNCTION_ID,
        "function_name": FUNCTION_NAME,
        "function_code": FUNCTION_CODE,
    },
    default=RegisteredResponse(
        service="compute",
        path="/v3/functions",
        method="POST",
        json=DEFAULT_RESPONSE_DOC,
    ),
)
