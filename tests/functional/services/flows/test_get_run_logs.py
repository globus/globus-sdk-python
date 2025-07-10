from globus_sdk.testing import load_response


def test_get_run_logs(flows_client):
    metadata = load_response(flows_client.get_run_logs).metadata

    resp = flows_client.get_run_logs(metadata["run_id"])
    assert resp.http_status == 200


def test_get_run_logs_paginated(flows_client):
    metadata = load_response(flows_client.get_run_logs, case="paginated").metadata

    paginator = flows_client.paginated.get_run_logs(metadata["run_id"])
    responses = list(paginator.pages())

    assert len(responses) == 2
    assert len(responses[0]["entries"]) == 10
    assert len(responses[1]["entries"]) == 2


def test_get_run_logs_manually_paginated(flows_client):
    metadata = load_response(flows_client.get_run_logs, case="paginated").metadata

    resp = flows_client.get_run_logs(metadata["run_id"])
    assert resp.http_status == 200
    assert resp["has_next_page"]
    assert "marker" in resp.data
    assert len(resp["entries"]) == 10

    resp2 = flows_client.get_run_logs(metadata["run_id"], marker=resp["marker"])
    assert resp2.http_status == 200
    assert not resp2["has_next_page"]
    assert len(resp2["entries"]) == 2
