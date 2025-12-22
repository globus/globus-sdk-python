from globus_sdk.testing import get_last_request, load_response


def test_cancel_task(client):
    meta = load_response(client.cancel_task).metadata

    res = client.cancel_task(meta["task_id"])
    assert res.http_status == 200

    req = get_last_request()
    assert req.body is None
