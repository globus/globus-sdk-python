import typing as t

import pytest

import globus_sdk


@pytest.fixture
def flows_client(no_retry_transport):
    return globus_sdk.FlowsClient(transport=no_retry_transport)


@pytest.fixture
def specific_flow_client_class(
    no_retry_transport,
) -> t.Type[globus_sdk.SpecificFlowClient]:
    class CustomSpecificFlowClient(globus_sdk.SpecificFlowClient):
        def __init__(self, **kwargs) -> None:
            kwargs["transport"] = no_retry_transport
            super().__init__(**kwargs)

    return CustomSpecificFlowClient
