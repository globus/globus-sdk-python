from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import FUNCTION_CODE, FUNCTION_ID, FUNCTION_NAME

FUNCTION_DOC = {
    "function_uuid": FUNCTION_ID,
    "function_name": FUNCTION_NAME,
    "function_code": FUNCTION_CODE,
    "description": "I just wanted to say hello.",
    "metadata": {"python_version": "3.12.6", "sdk_version": "2.28.1"},
}

RESPONSES = ResponseSet(
    metadata={
        "function_id": FUNCTION_ID,
        "function_name": FUNCTION_NAME,
        "function_code": FUNCTION_CODE,
    },
    default=RegisteredResponse(
        service="compute",
        path=f"/v2/functions/{FUNCTION_ID}",
        method="GET",
        json=FUNCTION_DOC,
    ),
)
