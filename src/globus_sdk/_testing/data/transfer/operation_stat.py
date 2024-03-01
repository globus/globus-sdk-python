from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import ENDPOINT_ID

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="transfer",
        method="GET",
        path=f"/operation/endpoint/{ENDPOINT_ID}/stat",
        json={
            "DATA_TYPE": "file",
            "group": "tutorial",
            "last_modified": "2023-12-18 16:52:50+00:00",
            "link_group": None,
            "link_last_modified": None,
            "link_size": None,
            "link_target": None,
            "link_user": None,
            "name": "file1.txt",
            "permissions": "0644",
            "size": 4,
            "type": "file",
            "user": "tutorial",
        },
    ),
)
