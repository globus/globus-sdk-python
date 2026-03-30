import pytest

from globus_sdk.experimental import TransferClientV2


@pytest.fixture
def client():
    client = TransferClientV2()
    with client.retry_config.tune(max_retries=0):
        yield client
