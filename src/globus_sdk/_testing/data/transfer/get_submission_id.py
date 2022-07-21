from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import SUBMISSION_ID

RESPONSES = ResponseSet(
    metadata={"submission_id": SUBMISSION_ID},
    default=RegisteredResponse(
        service="transfer",
        path="/submission_id",
        json={"value": SUBMISSION_ID},
    ),
)
