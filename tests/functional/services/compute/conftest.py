import pytest

import globus_sdk


@pytest.fixture
def compute_client_v2(no_retry_transport):
    class CustomComputeClientV2(globus_sdk.ComputeClientV2):
        default_transport_factory = no_retry_transport

    return CustomComputeClientV2()


@pytest.fixture
def compute_client_v3(no_retry_transport):
    class CustomComputeClientV3(globus_sdk.ComputeClientV3):
        default_transport_factory = no_retry_transport

    return CustomComputeClientV3()
