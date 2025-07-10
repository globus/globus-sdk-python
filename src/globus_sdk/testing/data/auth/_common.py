import uuid
from collections import namedtuple

_ErrorData = namedtuple("_ErrorData", ("error_id", "json", "metadata_include"))

_error_id = str(uuid.uuid1())
UNAUTHORIZED_AUTH_RESPONSE = _ErrorData(
    _error_id,
    {
        "errors": [
            {
                "status": "401",
                "id": _error_id,
                "code": "UNAUTHORIZED",
                "detail": "Call must be authenticated",
                "title": "Unauthorized",
            }
        ],
        "error_description": "Unauthorized",
        "error": "unauthorized",
    },
    {
        "http_status": 401,
        "code": "UNAUTHORIZED",
        "message": "Call must be authenticated",
    },
)

_error_id = str(uuid.uuid1())
FORBIDDEN_AUTH_RESPONSE = _ErrorData(
    _error_id,
    {
        "errors": [
            {
                "status": "403",
                "id": _error_id,
                "code": "FORBIDDEN",
                "detail": "Call must be authenticated",
                "title": "Unauthorized",
            }
        ],
        "error_description": "Unauthorized",
        "error": "unauthorized",
    },
    {
        "http_status": 403,
        "code": "FORBIDDEN",
        "message": "Call must be authenticated",
    },
)
