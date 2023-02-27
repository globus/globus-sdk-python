import pytest

from globus_sdk import GlobusSDKUsageError, RemovedInV4Warning
from globus_sdk.scopes import MutableScope
from globus_sdk.services.auth._common import stringify_requested_scopes


def test_scope_stringify_roundtrips_string():
    assert stringify_requested_scopes("foo") == "foo"


def test_scope_stringify_matches_str_of_mutable_scope():
    foo_scope = MutableScope("foo")
    # these asserts are nearly equivalent, but not quite the same
    # MutableScope.__str__ could -- at least, in theory -- change in the future
    assert stringify_requested_scopes(foo_scope) == str(foo_scope)
    assert stringify_requested_scopes(foo_scope) == "foo"


def test_scope_stringify_rejects_empty_string():
    with pytest.raises(
        GlobusSDKUsageError,
        match="requested_scopes cannot be the empty string or empty collection",
    ):
        stringify_requested_scopes("")


@pytest.mark.parametrize("collection_obj", ([], set(), ()))
def test_scope_stringify_rejects_empty_collection(collection_obj):
    with pytest.raises(
        GlobusSDKUsageError,
        match="requested_scopes cannot be the empty string or empty collection",
    ):
        stringify_requested_scopes(collection_obj)


def test_scope_stringify_handles_none_with_default():
    with pytest.warns(RemovedInV4Warning, match="Specify an explicit set of scopes"):
        scope_string = stringify_requested_scopes(None)
    assert (
        scope_string
        == "openid profile email urn:globus:auth:scope:transfer.api.globus.org:all"
    )
