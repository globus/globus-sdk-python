import globus_sdk
from globus_sdk.testing import load_response


def test_get_result_amqp_url(compute_client_v2: globus_sdk.ComputeClientV2):
    load_response(compute_client_v2.get_result_amqp_url)
    res = compute_client_v2.get_result_amqp_url()
    assert res.http_status == 200
    assert "connection_url" in res.data
