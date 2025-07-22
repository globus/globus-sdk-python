import pytest

import globus_sdk


@pytest.fixture
def compute_client_v2():
    client = globus_sdk.ComputeClientV2()
    with client.retry_config.tune(max_retries=0):
        yield client


@pytest.fixture
def compute_client_v3():
    client = globus_sdk.ComputeClientV3()
    with client.retry_config.tune(max_retries=0):
        yield client
