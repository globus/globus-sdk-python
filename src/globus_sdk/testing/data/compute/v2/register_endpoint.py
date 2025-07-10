from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import ENDPOINT_ID

DEFAULT_RESPONSE_DOC = {
    "endpoint_id": ENDPOINT_ID,
    "task_queue_info": {
        "connection_url": "amqps://user:password@mq.fqdn",
        "exchange": "some_exchange",
        "queue": "some_queue",
    },
    "result_queue_info": {
        "connection_url": "amqps://user:password@mq.fqdn",
        "exchange": "some_exchange",
        "queue": "some_queue",
        "queue_publish_kwargs": {},
    },
    "warnings": [],
}

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="compute",
        path="/v2/endpoints",
        method="POST",
        json=DEFAULT_RESPONSE_DOC,
    ),
)
