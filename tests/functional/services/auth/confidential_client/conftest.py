import pytest

import globus_sdk


@pytest.fixture
def auth_client():
    client = globus_sdk.ConfidentialAppAuthClient(
        "dummy_client_id", "dummy_client_secret"
    )
    with client.retry_config.tune(max_retries=0):
        yield client
