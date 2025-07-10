from responses.matchers import query_param_matcher

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import ENDPOINT_ID, ENDPOINT_ID_2, ENDPOINT_ID_3, NON_USER_ID, USER_ID

DEFAULT_RESPONSE_DOC = [
    {
        "uuid": ENDPOINT_ID,
        "name": "my-endpoint",
        "display_name": "My Endpoint",
        "owner": USER_ID,
    },
    {
        "uuid": ENDPOINT_ID_2,
        "name": "my-second-endpoint",
        "display_name": "My Second Endpoint",
        "owner": USER_ID,
    },
]

ANY_RESPONSE_DOC = [
    {
        "uuid": ENDPOINT_ID,
        "name": "my-endpoint",
        "display_name": "My Endpoint",
        "owner": USER_ID,
    },
    {
        "uuid": ENDPOINT_ID_2,
        "name": "my-second-endpoint",
        "display_name": "My Second Endpoint",
        "owner": USER_ID,
    },
    {
        "uuid": ENDPOINT_ID_3,
        "name": "public_endpoint",
        "display_name": "Public Endpoint",
        "owner": NON_USER_ID,
    },
]

RESPONSES = ResponseSet(
    metadata={
        "endpoint_id": ENDPOINT_ID,
        "endpoint_id_2": ENDPOINT_ID_2,
        "endpoint_id_3": ENDPOINT_ID_3,
    },
    default=RegisteredResponse(
        service="compute",
        path="/v2/endpoints",
        method="GET",
        json=DEFAULT_RESPONSE_DOC,
    ),
    any=RegisteredResponse(
        service="compute",
        path="/v2/endpoints",
        method="GET",
        json=ANY_RESPONSE_DOC,
        match=[query_param_matcher(params={"role": "any"})],
    ),
)
