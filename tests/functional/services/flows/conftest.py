import typing as t

import pytest

import globus_sdk


@pytest.fixture
def flows_client():
    client = globus_sdk.FlowsClient()
    with client.retry_configuration.tune(max_retries=0):
        yield client


@pytest.fixture
def specific_flow_client_class() -> t.Type[globus_sdk.SpecificFlowClient]:
    class CustomSpecificFlowClient(globus_sdk.SpecificFlowClient):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self.retry_configuration.max_retries = 0

    return CustomSpecificFlowClient
