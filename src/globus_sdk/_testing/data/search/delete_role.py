from globus_sdk._testing.models import RegisteredResponse, ResponseSet

INDEX_ID = "60d1160b-f016-40b0-8545-99619865873d"
IDENTITY_ID = "46bd0f56-e24f-11e5-a510-131bef46955c"
ROLE_ID = "MDMwMjM5"


RESPONSES = ResponseSet(
    metadata={"index_id": INDEX_ID, "identity_id": IDENTITY_ID, "role_id": ROLE_ID},
    default=RegisteredResponse(
        service="search",
        path=f"/v1/index/{INDEX_ID}/role/{ROLE_ID}",
        method="DELETE",
        json={
            "deleted": {
                "creation_date": "2022-01-26 21:53:06",
                "id": ROLE_ID,
                "index_id": INDEX_ID,
                "principal": f"urn:globus:auth:identity:{IDENTITY_ID}",
                "principal_type": "identity",
                "role_name": "writer",
            },
            "success": True,
        },
    ),
)
