from globus_sdk._testing.models import RegisteredResponse, ResponseSet

INDEX_ID = "60d1160b-f016-40b0-8545-99619865873d"
IDENTITY_IDS = [
    "ae332d86-d274-11e5-b885-b31714a110e9",
    "c699d42e-d274-11e5-bf75-1fc5bf53bb24",
]
ROLE_IDS = ["MDMwMjM5", "MDQ0ODYz"]


RESPONSES = ResponseSet(
    metadata={"index_id": INDEX_ID, "identity_ids": IDENTITY_IDS, "role_ids": ROLE_IDS},
    default=RegisteredResponse(
        service="search",
        path=f"/v1/index/{INDEX_ID}/role_list",
        json={
            "role_list": [
                {
                    "creation_date": "2021-11-09 20:26:45",
                    "id": ROLE_IDS[0],
                    "index_id": INDEX_ID,
                    "principal": "urn:globus:auth:identity:" + IDENTITY_IDS[0],
                    "principal_type": "identity",
                    "role_name": "owner",
                },
                {
                    "creation_date": "2022-01-24 15:33:41",
                    "id": ROLE_IDS[1],
                    "index_id": INDEX_ID,
                    "principal": "urn:globus:auth:identity:" + IDENTITY_IDS[1],
                    "principal_type": "identity",
                    "role_name": "writer",
                },
            ]
        },
    ),
)
