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
    not_found=RegisteredResponse(
        service="transfer",
        method="GET",
        path=f"/operation/endpoint/{ENDPOINT_ID}/stat",
        status=404,
        json={
            "code": "NotFound",
            "message": f"Path not found, Error (list)\nEndpoint: Globus Tutorial Collection 1 ({ENDPOINT_ID})\nServer: 100.26.231.26:443\nMessage: No such file or directory\n---\nDetails: Error: '~/foo' not found\\r\\n550-GlobusError: v=1 c=PATH_NOT_FOUND\\r\\n550-GridFTP-Errno: 2\\r\\n550-GridFTP-Reason: System error in stat\\r\\n550-GridFTP-Error-String: No such file or directory\\r\\n550 End.\\r\\n\n",  # noqa 501
            "request_id": "aaabbbccc",
            "resource": f"/operation/endpoint/{ENDPOINT_ID}/stat",
        },
    ),
    permission_denied=RegisteredResponse(
        service="transfer",
        method="GET",
        path=f"/operation/endpoint/{ENDPOINT_ID}/stat",
        status=403,
        json={
            "code": "EndpointPermissionDenied",
            "message": f"Denied by endpoint, Error (list)\nEndpoint: Globus Tutorial Collection 1 ({ENDPOINT_ID})\nServer: 100.26.231.26:443\nCommand: MLST /foo\nMessage: Fatal FTP Response\n---\nDetails: 500 Command failed : Path not allowed.\\r\\n\n",  # noqa 501
            "request_id": "aaabbbccc",
            "resource": f"/operation/endpoint/{ENDPOINT_ID}/stat",
        },
    ),
)
