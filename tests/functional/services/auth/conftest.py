import pytest

import globus_sdk


@pytest.fixture
def login_client(no_retry_transport):
    return globus_sdk.AuthLoginClient(transport=no_retry_transport)


@pytest.fixture
def service_client(no_retry_transport):
    return globus_sdk.AuthClient(transport=no_retry_transport)
