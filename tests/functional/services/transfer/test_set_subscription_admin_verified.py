import pytest

import globus_sdk
from globus_sdk.testing import load_response


def test_set_subscription_admin_verified(client):
    meta = load_response(client.set_subscription_admin_verified).metadata
    epid = meta["endpoint_id"]

    res = client.set_subscription_admin_verified(epid, True)
    assert res["code"] == "Updated"
    assert res["message"] == "Endpoint updated successfully"


def test_set_subscription_admin_verified_fails_no_admin_role(client):
    meta = load_response(
        client.set_subscription_admin_verified, case="no_admin_role"
    ).metadata
    epid = meta["endpoint_id"]

    with pytest.raises(globus_sdk.TransferAPIError) as excinfo:
        client.set_subscription_admin_verified(epid, True)

    assert excinfo.value.code == "PermissionDenied"
    assert len(excinfo.value.messages) == 1
    message = excinfo.value.messages[0]
    assert message == (
        "User does not have an admin role on the collection's subscription to set "
        "subscription_admin_verified"
    )


def test_set_subscription_admin_verified_fails_non_valid_verified_status(client):
    meta = load_response(
        client.set_subscription_admin_verified, case="non_valid_verified_status"
    ).metadata
    epid = meta["endpoint_id"]

    with pytest.raises(globus_sdk.TransferAPIError) as excinfo:
        client.set_subscription_admin_verified(epid, None)

    assert excinfo.value.code == "BadRequest"
    assert len(excinfo.value.messages) == 1
    message = excinfo.value.messages[0]
    assert message.startswith("Could not parse JSON: ")


def test_set_subscription_admin_verified_fails_non_subscribed_endpoint(client):
    meta = load_response(
        client.set_subscription_admin_verified, case="non_subscribed_endpoint"
    ).metadata
    epid = meta["endpoint_id"]

    with pytest.raises(globus_sdk.TransferAPIError) as excinfo:
        client.set_subscription_admin_verified(epid, True)

    assert excinfo.value.code == "BadRequest"
    assert len(excinfo.value.messages) == 1
    message = excinfo.value.messages[0]
    assert message == (
        "The collection must be associated with a subscription to "
        "set subscription_admin_verified"
    )


def test_set_subscription_admin_verified_fails_no_identities_in_session(client):
    meta = load_response(
        client.set_subscription_admin_verified, case="no_identities_in_session"
    ).metadata
    epid = meta["endpoint_id"]
    subid = meta["subscription_id"]

    with pytest.raises(globus_sdk.TransferAPIError) as excinfo:
        client.set_subscription_admin_verified(epid, True)

    assert excinfo.value.code == "BadRequest"
    assert len(excinfo.value.messages) == 1
    message = excinfo.value.messages[0]
    assert message == (
        "No manager or admin identities in session for high-assurance subscription "
        f"{subid}"
    )
