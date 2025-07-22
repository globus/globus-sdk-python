import pytest

import globus_sdk


@pytest.fixture
def client():
    # default fqdn for GCS client testing
    client = globus_sdk.GCSClient("abc.xyz.data.globus.org")
    with client.retry_config.tune(max_retries=0):
        yield client
