import pytest

import globus_sdk


@pytest.fixture
def client(no_retry_transport):
    return globus_sdk.TransferClient(transport=no_retry_transport)
