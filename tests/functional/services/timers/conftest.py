import pytest

import globus_sdk


@pytest.fixture
def client():
    return globus_sdk.TimersClient()
