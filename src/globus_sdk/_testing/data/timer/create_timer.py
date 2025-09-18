from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import (
    DEST_EP_ID,
    FLOW_ID,
    SOURCE_EP_ID,
    TIMER_ID,
    V2_FLOW_TIMER,
    V2_TRANSFER_TIMER,
)

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
    flow_timer_success=RegisteredResponse(
        service="timer",
        path="/v2/timer",
        method="POST",
        json={
            "timer": V2_FLOW_TIMER,
        },
        status=201,
        metadata={
            "timer_id": V2_FLOW_TIMER["job_id"],
            "flow_id": FLOW_ID,
            "callback_body": V2_FLOW_TIMER["callback_body"],
            "schedule": V2_FLOW_TIMER["schedule"],
        },
    ),
)
