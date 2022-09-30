from typing import Type

import pytest

import globus_sdk
from globus_sdk import SpecificFlowClient


@pytest.fixture
def flows_client(no_retry_transport):
    class CustomFlowsClient(globus_sdk.FlowsClient):
        transport_class = no_retry_transport

    return CustomFlowsClient()


@pytest.fixture
def specific_flow_client_class(no_retry_transport) -> Type[SpecificFlowClient]:
    class CustomSpecificFlowClient(globus_sdk.SpecificFlowClient):
        transport_class = no_retry_transport

    return CustomSpecificFlowClient
