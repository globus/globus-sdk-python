from globus_sdk import GCSClient
from globus_sdk.testing import load_response


def test_client_address_handling():
    # variants of the same location
    c1 = GCSClient("foo.data.globus.org")
    c2 = GCSClient("https://foo.data.globus.org")
    c3 = GCSClient("https://foo.data.globus.org/api/")
    # explicit subpath of /api/
    c4 = GCSClient("https://foo.data.globus.org/api/bar")
    # explicit construction can point at the root (rather than /api/)
    c5 = GCSClient("foo.data.globus.org")
    c5.base_url = "https://foo.data.globus.org/"

    # 1, 2, and 3 are all the same
    assert c1.base_url == c2.base_url
    assert c1.base_url == c3.base_url

    # 4 and 5 are different from the rest
    assert c4.base_url != c1.base_url
    assert c5.base_url != c1.base_url

    # 5 is the root of 1
    assert c1.base_url.startswith(c5.base_url)


def test_gcs_client_resource_server_and_endpoint_client_id():
    meta = load_response(GCSClient.get_gcs_info).metadata
    endpoint_client_id = meta["endpoint_client_id"]
    domain_name = meta["domain_name"]

    c = GCSClient(domain_name)
    assert c.endpoint_client_id == endpoint_client_id
    assert c.resource_server == endpoint_client_id
