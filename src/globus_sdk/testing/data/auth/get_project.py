import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

GUARDIANS_IDP_ID = str(uuid.uuid1())
STAR_LORD = {
    "identity_provider": GUARDIANS_IDP_ID,
    "identity_type": "login",
    "organization": "Guardians of the Galaxy",
    "status": "used",
    "id": str(uuid.uuid1()),
    "name": "Star Lord",
    "username": "star.lord@guardians.galaxy",
    # I thought it would be funny if he didn't get 'star.lord'
    # because someone else got it first
    "email": "star.lord2@guardians.galaxy",
}
ROCKET_RACCOON = {
    "identity_provider": GUARDIANS_IDP_ID,
    "identity_type": "login",
    "organization": "Guardians of the Galaxy",
    "status": "used",
    "id": str(uuid.uuid1()),
    "name": "Rocket",
    "username": "rocket@guardians.galaxy",
    # and think about it, who else would try to lay claim
    # to that email address?
    "email": "star.lord@guardians.galaxy",
}

GUARDIANS_PROJECT = {
    "admin_ids": [ROCKET_RACCOON["id"]],
    "contact_email": "support@guardians.galaxy",
    "display_name": "Guardians of the Galaxy Portal",
    "admin_group_ids": None,
    "id": str(uuid.uuid1()),
    "project_name": "Guardians of the Galaxy Portal",
    "admins": {
        "identities": [STAR_LORD, ROCKET_RACCOON],
        "groups": [],
    },
}

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path=f"/v2/api/projects/{GUARDIANS_PROJECT['id']}",
        json={"project": GUARDIANS_PROJECT},
        metadata={
            "project_id": GUARDIANS_PROJECT["id"],
        },
    )
)
