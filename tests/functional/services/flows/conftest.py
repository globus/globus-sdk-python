import typing as t

import pytest

import globus_sdk


@pytest.fixture
def flows_client(no_retry_transport):
    class CustomFlowsClient(globus_sdk.FlowsClient):
        transport_class = no_retry_transport

    return CustomFlowsClient()


@pytest.fixture
def specific_flow_client_class(
    no_retry_transport,
) -> t.Type[globus_sdk.SpecificFlowClient]:
    class CustomSpecificFlowClient(globus_sdk.SpecificFlowClient):
        transport_class = no_retry_transport

    return CustomSpecificFlowClient
