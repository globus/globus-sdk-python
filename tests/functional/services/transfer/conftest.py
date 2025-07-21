import pytest

import globus_sdk


@pytest.fixture
def client(no_retry_transport):
    class CustomTransferClient(globus_sdk.TransferClient):
        default_transport_factory = no_retry_transport

    return CustomTransferClient()
