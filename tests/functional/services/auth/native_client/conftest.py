import pytest

import globus_sdk


@pytest.fixture
def auth_client():
    client = globus_sdk.NativeAppAuthClient("dummy_client_id")
    with client.retry_configuration.tune(max_retries=0):
        yield client
