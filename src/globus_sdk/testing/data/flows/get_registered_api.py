from globus_sdk.testing.models import RegisteredResponse, ResponseSet

REGISTERED_API_ID = "9dc867a4-1c6d-46d9-911f-71c2ac67e38c"
OWNER_URN = "urn:globus:auth:identity:a1234567-1234-1234-1234-123456789abc"
ADMIN_URN = "urn:globus:auth:identity:b2345678-2345-2345-2345-234567890abc"
VIEWER_URN = "urn:globus:auth:identity:c3456789-3456-3456-3456-345678901abc"

REGISTERED_API_DOC = {
    "id": REGISTERED_API_ID,
    "name": "test-registered-api",
    "description": "A test registered API for testing purposes",
    "roles": {
        "owners": [OWNER_URN],
        "administrators": [ADMIN_URN],
        "viewers": [VIEWER_URN],
    },
    "target": {
        "type": "openapi",
        "openapi_version": "3.1",
        "destination": {
            "method": "get",
            "url": "https://example.com/api/v1/resource/{resource_id}",
        },
        "specification": {
            "summary": "Get Resource",
            "description": "Retrieve a resource by ID",
            "deprecated": False,
            "parameters": [
                {
                    "name": "resource_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                    "allowEmptyValue": False,
                    "allowReserved": False,
                    "deprecated": False,
                }
            ],
            "responses": {
                "200": {
                    "description": "A resource response",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ResourceResponse"}
                        }
                    },
                }
            },
            "security": [{"GlobusAuth": ["urn:globus:auth:scope:example.com:all"]}],
        },
        "transforms": None,
        "components": {
            "schemas": {
                "ResourceResponse": {
                    "type": "object",
                    "properties": {
                        "resource_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "The resource identifier",
                        },
                        "data": {
                            "type": "object",
                            "description": "The resource data",
                        },
                    },
                    "required": ["resource_id", "data"],
                    "additionalProperties": False,
                }
            }
        },
    },
    "data_templates": {
        "request": {
            "template": {
                "path": {"$T_ref": "$"},
            }
        },
        "response": {
            "2XX": {
                "template": {"$T_ref": "$.body"},
                "type": "success",
            },
            "default": {
                "template": {
                    "cause": {"$T_ref": "$.body"},
                    "exception": "ActionUnableToRun",
                },
                "type": "failure",
            },
        },
    },
    "state_input_schema": {
        "type": "object",
        "properties": {
            "resource_id": {"type": "string"},
        },
        "required": ["resource_id"],
    },
    "status": "ACTIVE",
    "subscription_id": "4fa609fc-14f6-4c62-acfd-680873d3b6fe",
    "created_timestamp": "2024-01-15T10:30:00+00:00",
    "edited_timestamp": None,
    "updated_timestamp": "2024-03-20T14:45:30+00:00",
    "scheduled_deletion_timestamp": None,
}

RESPONSES = ResponseSet(
    metadata={
        "registered_api_id": REGISTERED_API_ID,
        "name": REGISTERED_API_DOC["name"],
    },
    default=RegisteredResponse(
        service="flows",
        path=f"/registered_apis/{REGISTERED_API_ID}",
        json=REGISTERED_API_DOC,
    ),
)
