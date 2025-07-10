from globus_sdk._testing.models import RegisteredResponse, ResponseSet

DEFAULT_RESPONSE_DOC = {
    "queue_prefix": "some_prefix",
    "connection_url": "amqps://user:password@amqp.fqdn",
}

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="compute",
        path="/v2/get_amqp_result_connection_url",
        method="GET",
        json=DEFAULT_RESPONSE_DOC,
    ),
)
