from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import FUNCTION_ID

RESPONSES = ResponseSet(
    metadata={"function_id": FUNCTION_ID},
    default=RegisteredResponse(
        service="compute",
        path=f"/v2/functions/{FUNCTION_ID}",
        method="DELETE",
        json={"result": 302},
    ),
)
