import pytest

import globus_sdk


@pytest.fixture
def client():
    client = globus_sdk.SearchClient()
    with client.retry_configuration.tune(max_retries=0):
        yield client
