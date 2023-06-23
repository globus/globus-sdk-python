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

EVIL_TEST_PROJECT = {
    "admin_ids": [ROCKET_RACCOON["id"]],
    "contact_email": "eviltestproject@guardians.galaxy",
    "display_name": "Evil Test Project Full of Evil",
    "admin_group_ids": None,
    "id": str(uuid.uuid1()),
    "project_name": "Evil Test Project Full of Evil",
    "admins": {
        "identities": [ROCKET_RACCOON],
        "groups": [],
    },
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
        path="/v2/api/projects",
        json={"projects": [EVIL_TEST_PROJECT, GUARDIANS_PROJECT]},
        metadata={
            "project_ids": [EVIL_TEST_PROJECT["id"], GUARDIANS_PROJECT["id"]],
            "admin_map": {
                EVIL_TEST_PROJECT["id"]: [ROCKET_RACCOON["id"]],
                GUARDIANS_PROJECT["id"]: [STAR_LORD["id"], ROCKET_RACCOON["id"]],
            },
        },
    )
)
