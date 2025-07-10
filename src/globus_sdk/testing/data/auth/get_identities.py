import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import UNAUTHORIZED_AUTH_RESPONSE

_globus_at_globus_data = {
    "email": None,
    "id": "46bd0f56-e24f-11e5-a510-131bef46955c",
    "identity_provider": "7daddf46-70c5-45ee-9f0f-7244fe7c8707",
    "name": None,
    "organization": None,
    "status": "unused",
    "username": "globus@globus.org",
}
_sirosen_at_globus_data = {
    "email": "sirosen@globus.org",
    "id": "ae341a98-d274-11e5-b888-dbae3a8ba545",
    "identity_provider": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
    "name": "Stephen Rosen",
    "organization": "Globus Team",
    "status": "used",
    "username": "sirosen@globus.org",
}
_globus_at_globusid_data = {
    "email": "support@globus.org",
    "id": str(uuid.UUID(int=1)),
    "identity_provider": "41143743-f3c8-4d60-bbdb-eeecaba85bd9",
    "identity_type": "login",
    "name": "Globus Team",
    "organization": "University of Chicago",
    "status": "used",
    "username": "globus@globusid.org",
}

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path="/v2/api/identities",
        json={"identities": [_globus_at_globus_data]},
        metadata={
            "id": _globus_at_globus_data["id"],
            "username": _globus_at_globus_data["username"],
        },
    ),
    empty=RegisteredResponse(
        service="auth",
        path="/v2/api/identities",
        json={"identities": []},
    ),
    multiple=RegisteredResponse(
        service="auth",
        path="/v2/api/identities",
        json={"identities": [_globus_at_globus_data, _sirosen_at_globus_data]},
        metadata={
            "ids": [_globus_at_globus_data["id"], _sirosen_at_globus_data["id"]],
            "usernames": [
                _globus_at_globus_data["username"],
                _sirosen_at_globus_data["username"],
            ],
        },
    ),
    globusid=RegisteredResponse(
        service="auth",
        path="/v2/api/identities",
        json={"identities": [_globus_at_globusid_data]},
        metadata={
            "id": _globus_at_globusid_data["id"],
            "username": _globus_at_globusid_data["username"],
            "short_username": _globus_at_globusid_data["username"].partition("@")[0],
            "org": _globus_at_globusid_data["organization"],
        },
    ),
    sirosen=RegisteredResponse(
        service="auth",
        path="/v2/api/identities",
        json={"identities": [_sirosen_at_globus_data]},
        metadata={
            "id": _sirosen_at_globus_data["id"],
            "username": _sirosen_at_globus_data["username"],
            "org": _sirosen_at_globus_data["organization"],
        },
    ),
    unauthorized=RegisteredResponse(
        service="auth",
        path="/v2/api/identities",
        status=401,
        json=UNAUTHORIZED_AUTH_RESPONSE.json,
        metadata={"error_id": UNAUTHORIZED_AUTH_RESPONSE.error_id},
    ),
)
