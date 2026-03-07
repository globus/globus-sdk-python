import pytest

import globus_sdk
from globus_sdk.experimental.gcs_collection_client import GCSCollectionClient


@pytest.mark.parametrize("attrname", ["https", "data_access", "resource_server"])
def test_class_level_scopes_access_raises_useful_attribute_error(attrname):
    with pytest.raises(
        AttributeError,
        match=(
            f"It is not valid to attempt to access the '{attrname}' attribute of "
            "the GCSCollectionClient class"
        ),
    ):
        getattr(GCSCollectionClient.scopes, attrname)


def test_instance_level_scopes_access_ok():
    client = GCSCollectionClient("foo_id", "https://example.com/foo")

    assert client.resource_server == "foo_id"
    assert client.scopes.https == globus_sdk.Scope(
        "https://auth.globus.org/scopes/foo_id/https"
    )
    assert client.scopes.data_access == globus_sdk.Scope(
        "https://auth.globus.org/scopes/foo_id/data_access"
    )


def test_default_scope_is_https():
    client = GCSCollectionClient("foo_id", "https://example.com/foo")

    assert client.default_scope_requirements == [
        globus_sdk.Scope("https://auth.globus.org/scopes/foo_id/https")
    ]
