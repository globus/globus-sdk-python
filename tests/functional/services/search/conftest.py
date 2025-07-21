import pytest

import globus_sdk


@pytest.fixture
def client(no_retry_transport):
    class CustomSearchClient(globus_sdk.SearchClient):
        default_transport_factory = no_retry_transport

    return CustomSearchClient()
