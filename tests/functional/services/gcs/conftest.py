import pytest

from globus_sdk import GCSClient


@pytest.fixture
def client(no_retry_transport):
    class CustomGCSClient(GCSClient):
        default_transport_factory = no_retry_transport

    # default fqdn for GCS client testing
    return CustomGCSClient("abc.xyz.data.globus.org")
