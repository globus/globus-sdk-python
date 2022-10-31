import pytest

import globus_sdk


@pytest.fixture
def client(no_retry_transport):
    class CustomTransferClient(globus_sdk.TransferClient):
        transport_class = no_retry_transport

    return CustomTransferClient()
