import pytest

import globus_sdk


@pytest.fixture
def auth_client(no_retry_transport):
    return globus_sdk.NativeAppAuthClient(
        "dummy_client_id", transport=no_retry_transport
    )
