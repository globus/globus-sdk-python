from globus_sdk._testing import load_response


def test_endpoint_manager_task_successful_transfers(client):
    meta = load_response(client.endpoint_manager_task_successful_transfers).metadata

    response = client.endpoint_manager_task_successful_transfers(meta["task_id"])

    assert response.http_status == 200
    assert response["DATA_TYPE"] == "successful_transfers"
