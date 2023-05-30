from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import ENDPOINT_ID

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="transfer",
        method="POST",
        path=f"/operation/endpoint/{ENDPOINT_ID}/mkdir",
        json={
            "DATA_TYPE": "mkdir_result",
            "code": "DirectoryCreated",
            "message": "The directory was created successfully",
            "request_id": "ShbIUzrWT",
            "resource": f"/operation/endpoint/{ENDPOINT_ID}/mkdir",
        },
    ),
)
