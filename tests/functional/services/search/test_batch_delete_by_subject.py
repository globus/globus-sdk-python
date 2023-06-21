from globus_sdk._testing import load_response


def test_batch_delete_by_subject(client):
    meta = load_response(client.batch_delete_by_subject).metadata

    res = client.batch_delete_by_subject(
        meta["index_id"],
        {
            "subjects": [
                "very-cool-document",
                "less-cool-document",
                "document-wearing-sunglasses",
            ]
        },
    )
    assert res.http_status == 200

    assert res["task_id"] == meta["task_id"]
