import pytest

import globus_sdk


@pytest.fixture
def login_client():
    client = globus_sdk.AuthLoginClient()
    with client.retry_config.tune(max_retries=0):
        yield client


@pytest.fixture
def service_client():
    client = globus_sdk.AuthClient()
    with client.retry_config.tune(max_retries=0):
        yield client
