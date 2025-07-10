import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

CREDENTIAL = {
    "name": "foo",
    "id": str(uuid.uuid1()),
    "created": "2023-10-21T22:46:15.845937+00:00",
    "client": "7dee4432-0297-4989-ad23-a2b672a52b12",
    "secret": None,
}

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        method="DELETE",
        path=f"/v2/api/clients/{CREDENTIAL['client']}/credentials/{CREDENTIAL['id']}",
        json={"credential": CREDENTIAL},
        metadata={
            "credential_id": CREDENTIAL["id"],
            "client_id": CREDENTIAL["client"],
        },
    ),
)
