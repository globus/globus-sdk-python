from globus_sdk._testing.models import RegisteredResponse, ResponseSet

INDEX_ID = "60d1160b-f016-40b0-8545-99619865873d"


RESPONSES = ResponseSet(
    metadata={"index_id": INDEX_ID},
    default=RegisteredResponse(
        service="search",
        path=f"/v1/index/{INDEX_ID}/search",
        method="POST",
        json={
            "@datatype": "GSearchResult",
            "@version": "2017-09-01",
            "count": 1,
            "gmeta": [
                {
                    "@datatype": "GMetaResult",
                    "@version": "2019-08-27",
                    "entries": [
                        {
                            "content": {"foo": "bar"},
                            "entry_id": None,
                            "matched_principal_sets": [],
                        }
                    ],
                    "subject": "foo-bar",
                }
            ],
            "has_next_page": True,
            "offset": 0,
            "total": 10,
        },
    ),
)
