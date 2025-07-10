from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import FUNCTION_CODE, FUNCTION_ID, FUNCTION_NAME

RESPONSES = ResponseSet(
    metadata={
        "function_id": FUNCTION_ID,
        "function_name": FUNCTION_NAME,
        "function_code": FUNCTION_CODE,
    },
    default=RegisteredResponse(
        service="compute",
        path="/v2/functions",
        method="POST",
        json={"function_uuid": FUNCTION_ID},
    ),
)
