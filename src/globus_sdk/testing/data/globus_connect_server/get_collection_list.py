import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

identity_id = str(uuid.uuid4())
collection_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
gateway_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
display_names = ["Happy Fun Collection Name 1", "Happy Fun Collection Name 2"]

RESPONSES = ResponseSet(
    metadata={
        "identity_id": identity_id,
        "collection_ids": collection_ids,
        "gateway_ids": gateway_ids,
        "display_names": display_names,
    },
    default=RegisteredResponse(
        service="gcs",
        path="/collections",
        json={
            "DATA_TYPE": "result#1.0.0",
            "code": "success",
            "detail": "success",
            "http_response_code": 200,
            "data": [
                {
                    "DATA_TYPE": "collection#1.0.0",
                    "public": True,
                    "id": collection_ids[0],
                    "display_name": display_names[0],
                    "identity_id": identity_id,
                    "collection_type": "mapped",
                    "storage_gateway_id": gateway_ids[0],
                    "require_high_assurance": False,
                    "high_assurance": False,
                    "authentication_assurance_timeout": 15840,
                    "authentication_timeout_mins": 15840,
                },
                {
                    "DATA_TYPE": "collection#1.0.0",
                    "public": True,
                    "id": collection_ids[1],
                    "display_name": display_names[1],
                    "identity_id": identity_id,
                    "collection_type": "mapped",
                    "storage_gateway_id": gateway_ids[1],
                    "require_high_assurance": False,
                    "high_assurance": False,
                    "authentication_assurance_timeout": 15840,
                    "authentication_timeout_mins": 15840,
                },
            ],
        },
    ),
    forbidden=RegisteredResponse(
        service="gcs",
        path="/collections",
        status=403,
        json={
            "code": "permission_denied",
            "http_response_code": 403,
            "DATA_TYPE": "result#1.0.0",
            "detail": None,
            "message": "Could not list collections. Insufficient permissions",
            "data": [],
            "has_next_page": False,
            "marker": "",
        },
    ),
)
