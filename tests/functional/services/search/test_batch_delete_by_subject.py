import json

from globus_sdk._testing import get_last_request, load_response


def test_batch_delete_by_subject(client):
    meta = load_response(client.batch_delete_by_subject).metadata
    input_subjects = [
        "very-cool-document",
        "less-cool-document",
        "document-wearing-sunglasses",
    ]

    res = client.batch_delete_by_subject(meta["index_id"], subjects=input_subjects)
    assert res.http_status == 200

    assert res["task_id"] == meta["task_id"]

    req = get_last_request()
    sent_data = json.loads(req.body)
    assert sent_data == {"subjects": input_subjects}


def test_batch_delete_by_subject_accepts_string(client):
    """
    Test the handling for a single string.

    We want to ensure that
        subjects="mydoc"
    parses the same as
        subjects=["mydoc"]
    *not* as
        subjects=["m", "y", "d", "o", "c"]
    """
    meta = load_response(client.batch_delete_by_subject).metadata
    input_subject = "very-cool-document"

    res = client.batch_delete_by_subject(meta["index_id"], subjects=input_subject)
    assert res.http_status == 200

    assert res["task_id"] == meta["task_id"]

    req = get_last_request()
    sent_data = json.loads(req.body)
    assert sent_data == {"subjects": [input_subject]}


def test_batch_delete_by_subject_allows_additional_params(client):
    meta = load_response(client.batch_delete_by_subject).metadata
    input_subjects = [
        "very-cool-document",
        "less-cool-document",
        "document-wearing-sunglasses",
    ]

    res = client.batch_delete_by_subject(
        meta["index_id"],
        subjects=input_subjects,
        additional_params={"foo": "snork"},
    )
    assert res.http_status == 200

    assert res["task_id"] == meta["task_id"]

    req = get_last_request()
    sent_data = json.loads(req.body)
    assert sent_data == {"subjects": input_subjects, "foo": "snork"}
