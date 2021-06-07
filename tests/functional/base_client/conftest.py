import pytest

import globus_sdk


@pytest.fixture
def client():
    class CustomClient(globus_sdk.client.BaseClient):
        service_name = "foo"

    return CustomClient()
