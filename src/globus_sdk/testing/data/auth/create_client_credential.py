import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

NEW_CREDENTIAL_NAME = str(uuid.uuid4()).replace("-", "")

CREDENTIAL = {
    "name": "foo",
    "id": str(uuid.uuid1()),
    "created": "2023-10-21T22:46:15.845937+00:00",
    "client": str(uuid.uuid1()),
    "secret": "abc123",
}


RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        method="POST",
        path=f"/v2/api/clients/{CREDENTIAL['client']}/credentials",
        json={"credential": CREDENTIAL},
        metadata={
            "credential_id": CREDENTIAL["id"],
            "client_id": CREDENTIAL["client"],
            "name": CREDENTIAL["name"],
        },
    ),
    name=RegisteredResponse(
        service="auth",
        method="POST",
        path=f"/v2/api/clients/{CREDENTIAL['client']}/credentials",
        json={
            "credential": {
                **CREDENTIAL,
                "name": NEW_CREDENTIAL_NAME,
            }
        },
        metadata={
            "name": NEW_CREDENTIAL_NAME,
            "client_id": CREDENTIAL["client"],
        },
    ),
)
