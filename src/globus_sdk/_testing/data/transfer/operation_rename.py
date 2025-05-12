from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import ENDPOINT_ID

RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="transfer",
        method="POST",
        path=f"/v0.10/operation/endpoint/{ENDPOINT_ID}/rename",
        json={
            "DATA_TYPE": "result",
            "code": "FileRenamed",
            "message": "File or directory renamed successfully",
            "request_id": "ShbIUzrWT",
            "resource": f"/v0.10/operation/endpoint/{ENDPOINT_ID}/rename",
        },
    ),
)
