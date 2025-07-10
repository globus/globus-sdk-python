import pytest

import globus_sdk
from globus_sdk.testing import load_response


def test_set_subscription_id(client):
    meta = load_response(client.set_subscription_id).metadata
    epid = meta["endpoint_id"]

    res = client.set_subscription_id(epid, "DEFAULT")
    assert res["code"] == "Updated"
    assert res["message"] == "Endpoint updated successfully"


def test_set_subscription_id_fails_notfound(client):
    meta = load_response(client.set_subscription_id, case="not_found").metadata
    epid = meta["endpoint_id"]

    with pytest.raises(globus_sdk.TransferAPIError) as excinfo:
        client.set_subscription_id(epid, "DEFAULT")

    assert excinfo.value.code == "EndpointNotFound"
    assert excinfo.value.messages == [f"No such endpoint '{epid}'"]


def test_set_subscription_id_fails_multi(client):
    meta = load_response(
        client.set_subscription_id, case="multi_subscriber_cannot_use_default"
    ).metadata
    epid = meta["endpoint_id"]

    with pytest.raises(globus_sdk.TransferAPIError) as excinfo:
        client.set_subscription_id(epid, "DEFAULT")

    assert excinfo.value.code == "BadRequest"
    assert len(excinfo.value.messages) == 1
    message = excinfo.value.messages[0]
    assert message.startswith("Please specify the subscription ID to use.")
