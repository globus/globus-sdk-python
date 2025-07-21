import pytest

import globus_sdk


@pytest.fixture
def client(no_retry_transport):
    # default fqdn for GCS client testing
    return globus_sdk.GCSClient("abc.xyz.data.globus.org", transport=no_retry_transport)
