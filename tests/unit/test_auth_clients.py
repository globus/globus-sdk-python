import uuid

import pytest

from globus_sdk import AuthClient, ConfidentialAppAuthClient, NativeAppAuthClient

CLIENT_ID_UUID = uuid.uuid4()
CLIENT_ID_STR = str(CLIENT_ID_UUID)


def test_base_auth_client_does_not_require_client_id():
    client = AuthClient()
    assert client.client_id is None


@pytest.mark.parametrize(
    "client_type", (AuthClient, ConfidentialAppAuthClient, NativeAppAuthClient)
)
@pytest.mark.parametrize("pass_value_as", ("str", "uuid"))
def test_can_use_uuid_or_str_for_client_id(client_type, pass_value_as):
    pass_value = CLIENT_ID_UUID if pass_value_as == "uuid" else CLIENT_ID_STR

    if client_type in (AuthClient, NativeAppAuthClient):
        client = client_type(client_id=pass_value)
    elif client_type is ConfidentialAppAuthClient:
        client = ConfidentialAppAuthClient(pass_value, "bogus_secret")
    else:
        raise NotImplementedError

    assert client.client_id == CLIENT_ID_STR
