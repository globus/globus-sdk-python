import unittest.mock
import uuid

import pytest

import globus_sdk

CLIENT_ID_UUID = uuid.uuid4()
CLIENT_ID_STR = str(CLIENT_ID_UUID)


@pytest.mark.parametrize(
    "client_type",
    (
        globus_sdk.AuthLoginClient,
        globus_sdk.ConfidentialAppAuthClient,
        globus_sdk.NativeAppAuthClient,
    ),
)
@pytest.mark.parametrize(
    "pass_value", (CLIENT_ID_STR, CLIENT_ID_UUID), ids=("str", "uuid")
)
def test_can_use_uuid_or_str_for_client_id(client_type, pass_value):
    if client_type in (globus_sdk.AuthLoginClient, globus_sdk.NativeAppAuthClient):
        client = client_type(client_id=pass_value)
    elif client_type is globus_sdk.ConfidentialAppAuthClient:
        client = globus_sdk.ConfidentialAppAuthClient(pass_value, "bogus_secret")
    else:
        raise NotImplementedError

    assert client.client_id == CLIENT_ID_STR


def test_native_app_auth_client_rejects_authorizer():
    authorizer = unittest.mock.Mock()
    with pytest.raises(TypeError):
        globus_sdk.NativeAppAuthClient(CLIENT_ID_UUID, authorizer=authorizer)


def test_confidential_app_auth_client_rejects_authorizer():
    authorizer = unittest.mock.Mock()
    with pytest.raises(TypeError):
        globus_sdk.ConfidentialAppAuthClient(
            CLIENT_ID_UUID, "foo-secret", authorizer=authorizer
        )


def test_service_client_rejects_client_id():
    # init will warn because a value is being passed
    with pytest.raises(TypeError):
        globus_sdk.AuthClient(client_id=CLIENT_ID_STR)
