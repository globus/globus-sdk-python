from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import ENDPOINT_ID

DEFAULT_RESPONSE_DOC = {
    "endpoint_id": ENDPOINT_ID,
    "lock_expiration_timestamp": "2021-07-01T00:00:00.000000",
}

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="compute",
        path=f"/v2/endpoints/{ENDPOINT_ID}/lock",
        method="POST",
        json=DEFAULT_RESPONSE_DOC,
    ),
)
