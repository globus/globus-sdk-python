from globus_sdk._testing.models import RegisteredResponse, ResponseSet

_DATA_ACCESS = (
    "https://auth.globus.org/scopes/542a86fc-1766-450d-841f-065488a2ec01/data_access"
)

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path="/v2/api/identities/8ca28797-3541-4a5d-a264-05b00f91e608/consents",
        json={
            "consents": [
                {
                    "created": "2022-09-21T17:10:14.270581+00:00",
                    "id": 142632,
                    "status": "approved",
                    "updated": "2022-09-21T17:10:14.270581+00:00",
                    "allows_refresh": True,
                    "dependency_path": [142632],
                    "scope_name": "urn:globus:auth:scope:transfer.api.globus.org:all",
                    "atomically_revocable": False,
                    "effective_identity": "8ca28797-3541-4a5d-a264-05b00f91e608",
                    "auto_approved": False,
                    "last_used": "2024-03-18T17:34:04.719126+00:00",
                    "scope": "89ecabba-4acf-4e2e-a98d-ce592ccc2818",
                    "client": "065db752-2f43-4fe1-a633-2ee68c9da889",
                },
                {
                    "created": "2024-03-18T17:32:51.496893+00:00",
                    "id": 433892,
                    "status": "approved",
                    "updated": "2024-03-18T17:32:51.496893+00:00",
                    "allows_refresh": True,
                    "dependency_path": [142632, 433892],
                    "scope_name": _DATA_ACCESS,
                    "atomically_revocable": True,
                    "effective_identity": "8ca28797-3541-4a5d-a264-05b00f91e608",
                    "auto_approved": False,
                    "last_used": "2024-03-18T17:33:05.178254+00:00",
                    "scope": "fe334c19-4fe6-4d03-ac73-8992beb231b6",
                    "client": "2fbdda78-a599-4cb5-ac3d-1fbcfbc6a754",
                },
            ]
        },
        metadata={
            "identity_id": "8ca28797-3541-4a5d-a264-05b00f91e608",
        },
    ),
)
