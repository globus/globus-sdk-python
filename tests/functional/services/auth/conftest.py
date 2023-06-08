import pytest

import globus_sdk


@pytest.fixture
def client(no_retry_transport):
    class CustomAuthClient(globus_sdk.AuthClient):
        transport_class = no_retry_transport

    return CustomAuthClient()
