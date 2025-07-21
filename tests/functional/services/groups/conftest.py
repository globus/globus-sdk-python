import pytest

import globus_sdk


@pytest.fixture
def groups_client(no_retry_transport):
    class CustomGroupsClient(globus_sdk.GroupsClient):
        default_transport_factory = no_retry_transport

    return CustomGroupsClient()


@pytest.fixture
def groups_manager(groups_client):
    return globus_sdk.GroupsManager(groups_client)
