import pytest

import globus_sdk


@pytest.fixture
def groups_client():
    client = globus_sdk.GroupsClient()
    with client.retry_config.tune(max_retries=0):
        yield client


@pytest.fixture
def groups_manager(groups_client):
    return globus_sdk.GroupsManager(groups_client)
