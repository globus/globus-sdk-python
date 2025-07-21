import pytest

import globus_sdk


@pytest.fixture
def compute_client_v2(no_retry_transport):
    return globus_sdk.ComputeClientV2(transport=no_retry_transport)


@pytest.fixture
def compute_client_v3(no_retry_transport):
    return globus_sdk.ComputeClientV3(transport=no_retry_transport)
