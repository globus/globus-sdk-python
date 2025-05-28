import pytest

from globus_sdk import GlobusSDKUsageError
from globus_sdk.scopes import Scope
from globus_sdk.services.auth._common import stringify_requested_scopes


def test_scope_stringify_roundtrips_string():
    assert stringify_requested_scopes("foo") == "foo"


def test_scope_stringify_matches_str_of_scope_object():
    foo_scope = Scope("foo")
    # these asserts are nearly equivalent, but not quite the same
    # Scope.__str__ could -- at least, in theory -- change in the future
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
