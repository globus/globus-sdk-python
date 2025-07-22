import pytest

import globus_sdk


@pytest.fixture
def client_class():
    class CustomClient(globus_sdk.BaseClient):
        service_name = "foo"

    return CustomClient


@pytest.fixture
def client(client_class):
    return client_class()
