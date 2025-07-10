from globus_sdk._testing.models import RegisteredResponse, ResponseSet

globusid_idp = {
    "short_name": "globusid",
    "id": "41143743-f3c8-4d60-bbdb-eeecaba85bd9",
    "alternative_names": [],
    "domains": ["globusid.org"],
    "name": "Globus ID",
}

globus_staff_idp = {
    "short_name": "globus.org",
    "id": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
    "alternative_names": [],
    "domains": ["globus.org"],
    "name": "Globus Staff",
}

RESPONSES = ResponseSet(
    default=RegisteredResponse(
        service="auth",
        path="/v2/api/identity_providers",
        json={"identity_providers": [globusid_idp, globus_staff_idp]},
        metadata={
            "ids": [globusid_idp["id"], globus_staff_idp["id"]],
            "domains": [globusid_idp["domains"][0], globus_staff_idp["domains"][0]],
        },
    ),
    globusid=RegisteredResponse(
        service="auth",
        path="/v2/api/identity_providers",
        json={"identity_providers": [globusid_idp]},
        metadata={"id": globusid_idp["id"], "domains": globusid_idp["domains"]},
    ),
    globus_staff=RegisteredResponse(
        service="auth",
        path="/v2/api/identity_providers",
        json={"identity_providers": [globus_staff_idp]},
        metadata={"id": globus_staff_idp["id"], "domains": globus_staff_idp["domains"]},
    ),
)
