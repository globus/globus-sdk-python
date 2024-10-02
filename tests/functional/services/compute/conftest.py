import pytest

import globus_sdk


@pytest.fixture
def compute_client(no_retry_transport):
    class CustomComputeClient(globus_sdk.ComputeClient):
        transport_class = no_retry_transport

    return CustomComputeClient()
