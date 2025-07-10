from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import ENDPOINT_ID, SUBSCRIPTION_ID

ENDPOINT_CONFIG = """
display_name: My Endpoint
engine:
  type: GlobusComputeEngine
"""

DEFAULT_RESPONSE_DOC = {
    "uuid": ENDPOINT_ID,
    "name": "my-endpoint",
    "display_name": "My Endpoint",
    "multi_user": False,
    "public": False,
    "endpoint_config": ENDPOINT_CONFIG.strip(),
    "user_config_template": "",
    "user_config_schema": {},
    "description": "My endpoint description",
    "hostname": "my-hostname",
    "local_user": "user1",
    "ip_address": "140.221.112.13",
    "endpoint_version": "2.31.0",
    "sdk_version": "2.31.0",
    "subscription_uuid": SUBSCRIPTION_ID,
}

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="compute",
        path=f"/v2/endpoints/{ENDPOINT_ID}",
        method="GET",
        json=DEFAULT_RESPONSE_DOC,
    ),
)
