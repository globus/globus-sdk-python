import pytest

import globus_sdk


@pytest.fixture
def auth_client(no_retry_transport):
    return globus_sdk.ConfidentialAppAuthClient(
        "dummy_client_id", "dummy_client_secret", transport=no_retry_transport
    )
