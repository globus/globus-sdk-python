import pytest

import globus_sdk


@pytest.fixture
def auth_client(no_retry_transport):
    class CustomAuthClient(globus_sdk.NativeAppAuthClient):
        default_transport_factory = no_retry_transport

    return CustomAuthClient("dummy_client_id")
