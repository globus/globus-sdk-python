import pytest

import globus_sdk


@pytest.fixture
def groups_client(no_retry_transport):
    return globus_sdk.GroupsClient(transport=no_retry_transport)


@pytest.fixture
def groups_manager(groups_client):
    return globus_sdk.GroupsManager(groups_client)
