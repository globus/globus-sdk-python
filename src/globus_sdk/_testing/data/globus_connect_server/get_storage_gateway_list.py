from globus_sdk._testing.models import RegisteredResponse, ResponseSet

GATEWAY_IDS = [
    "a0cbde58-0183-11ea-92bd-9cb6d0d9fd63",
    "6840c8ba-eb98-11e9-b89c-9cb6d0d9fd63",
]

RESPONSES = ResponseSet(
    metadata={"ids": GATEWAY_IDS},
    default=RegisteredResponse(
        service="gcs",
        path="/storage_gateways",
        json={
            "DATA_TYPE": "result#1.0.0",
            "code": "success",
            "detail": "success",
            "http_response_code": 200,
            "data": [
                {
                    "DATA_TYPE": "storage_gateway#1.0.0",
                    "id": GATEWAY_IDS[0],
                    "display_name": "example gateway 1",
                    "connector_id": "145812c8-decc-41f1-83cf-bb2a85a2a70b",
                    "high_assurance": False,
                    "authentication_assurance_timeout": 15840,
                    "authentication_timeout_mins": 15840,
                    "allowed_domains": ["example.edu"],
                    "mapping": "username_without_domain",
                    "require_high_assurance": False,
                    "restrict_paths": {
                        "DATA_TYPE": "path_restrictions#1.0.0",
                        "read": ["/"],
                    },
                    "policies": {
                        "DATA_TYPE": "posix_storage_gateway#1.0.0",
                        "groups_allow": ["globus"],
                        "groups_deny": ["nonglobus"],
                    },
                    "users_allow": ["user1"],
                    "users_deny": ["user2"],
                },
                {
                    "DATA_TYPE": "storage_gateway#1.0.0",
                    "id": GATEWAY_IDS[1],
                    "display_name": "example gateway 2",
                    "connector_id": "145812c8-decc-41f1-83cf-bb2a85a2a70b",
                    "high_assurance": False,
                    "authentication_assurance_timeout": 15840,
                    "authentication_timeout_mins": 15840,
                    "allowed_domains": ["example.edu"],
                    "mapping": "username_without_domain",
                    "require_high_assurance": False,
                    "policies": {
                        "DATA_TYPE": "posix_storage_gateway#1.0.0",
                        "groups_allow": [],
                        "groups_deny": [],
                    },
                    "users_allow": [],
                    "users_deny": [],
                },
            ],
        },
    ),
)
