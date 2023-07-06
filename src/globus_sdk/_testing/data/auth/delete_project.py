import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

project_id = str(uuid.uuid1())
star_lord = {
    "identity_provider": str(uuid.uuid1()),
    "identity_type": "login",
    "organization": "Guardians of the Galaxy",
    "status": "used",
    "id": str(uuid.uuid1()),
    "name": "Star Lord",
    "username": "star.lord@guardians.galaxy",
    "email": "star.lord2@guardians.galaxy",
}

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path=f"/v2/api/projects/{project_id}",
        method="DELETE",
        json={
            "project": {
                "contact_email": "support@globus.org",
                "id": project_id,
                "admins": {
                    "identities": [star_lord],
                    "groups": [],
                },
                "project_name": "Guardians of the Galaxy",
                "admin_ids": [star_lord["id"]],
                "admin_group_ids": None,
                "display_name": "Guardians of the Galaxy",
            }
        },
        metadata={
            "id": project_id,
            "admin_id": star_lord["id"],
        },
    ),
)
