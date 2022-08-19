import pytest

import globus_sdk


@pytest.fixture
def flows_client(no_retry_transport):
    class CustomFlowsClient(globus_sdk.FlowsClient):
        transport_class = no_retry_transport

    return CustomFlowsClient()
