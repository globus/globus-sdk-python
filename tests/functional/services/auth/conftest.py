import pytest

import globus_sdk


@pytest.fixture
def login_client(no_retry_transport):
    class CustomAuthClient(globus_sdk.AuthLoginClient):
        default_transport_factory = no_retry_transport

    return CustomAuthClient()


@pytest.fixture
def service_client(no_retry_transport):
    class CustomAuthClient(globus_sdk.AuthClient):
        default_transport_factory = no_retry_transport

    return CustomAuthClient()
