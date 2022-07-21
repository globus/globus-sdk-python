from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import ENDPOINT_ID

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="transfer",
        method="POST",
        path="/endpoint",
        json={
            "DATA_TYPE": "endpoint_create_result",
            "display_name": "my cool endpoint",
            "code": "Created",
            "globus_connect_setup_key": None,
            "id": ENDPOINT_ID,
            "message": "Endpoint created successfully",
            "request_id": "d4MqMwFJ9",
            "resource": "/endpoint",
        },
    ),
)
