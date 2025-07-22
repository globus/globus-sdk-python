import pytest

import globus_sdk
from globus_sdk.testing import RegisteredResponse


def test_transfer_client_will_retry_ordinary_502(client, mocksleep):
    # turn on retries (fixture defaults off)
    client.retry_config.max_retries = 1

    RegisteredResponse(service="transfer", path="/foo", status=502, body="Uh-oh!").add()
    RegisteredResponse(service="transfer", path="/foo", json={"status": "ok"}).add()

    # no sign of an error in the client
    res = client.get("/foo")
    assert res.http_status == 200
    assert res["status"] == "ok"

    # there was a sleep (retry was triggered)
    mocksleep.assert_called_once()


def test_transfer_client_will_not_retry_endpoint_error(client, mocksleep):
    # turn on retries (fixture defaults off)
    client.retry_config.max_retries = 1

    RegisteredResponse(
        service="transfer",
        path="/do_a_gcp_thing",
        status=502,
        json={
            "HTTP status": "502",
            "code": "ExternalError.DirListingFailed.GCDisconnected",
            "error_name": "Transfer API Error",
            "message": "The GCP endpoint is not currently connected to Globus",
            "request_id": "rhvcR0aHX",
        },
    ).add()
    RegisteredResponse(
        service="transfer", path="/do_a_gcp_thing", json={"status": "ok"}
    ).add()

    # no sign of an error in the client
    with pytest.raises(globus_sdk.TransferAPIError) as excinfo:
        client.get("/do_a_gcp_thing")
    assert excinfo.value.http_status == 502

    # there was no sleep (retry was not triggered)
    mocksleep.assert_not_called()
