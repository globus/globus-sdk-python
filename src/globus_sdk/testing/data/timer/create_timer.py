from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import DEST_EP_ID, SOURCE_EP_ID, TIMER_ID, V2_TRANSFER_TIMER

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="timer",
        path="/v2/timer",
        method="POST",
        json={
            "timer": V2_TRANSFER_TIMER,
        },
        status=201,
        metadata={
            "timer_id": TIMER_ID,
            "source_endpoint": SOURCE_EP_ID,
            "destination_endpoint": DEST_EP_ID,
        },
    ),
)
