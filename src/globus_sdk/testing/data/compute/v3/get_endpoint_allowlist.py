from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import ENDPOINT_ID, FUNCTION_ID, FUNCTION_ID_2

DEFAULT_RESPONSE_DOC = {
    "endpoint_id": ENDPOINT_ID,
    "restricted": True,
    "functions": [FUNCTION_ID, FUNCTION_ID_2],
}

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="compute",
        path=f"/v3/endpoints/{ENDPOINT_ID}/allowed_functions",
        method="GET",
        json=DEFAULT_RESPONSE_DOC,
    ),
)
