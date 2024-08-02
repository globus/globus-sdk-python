import pytest

from globus_sdk.scopes import MutableScope, Scope, scopes_to_scope_list, scopes_to_str


def test_scopes_to_str_roundtrip_simple_str():
    assert scopes_to_str("scope1") == "scope1"


def test_scopes_to_str_stringifies_single_scope():
    assert scopes_to_str(Scope("scope1")) == "scope1"


@pytest.mark.parametrize(
    "scope_collection",
    (
        ("scope1",),
        ["scope1"],
        {"scope1"},
        (s for s in ["scope1"]),
    ),
)
def test_scopes_to_str_roundtrip_simple_str_in_collection(scope_collection):
    assert scopes_to_str(scope_collection) == "scope1"


@pytest.mark.parametrize(
    "scope_collection, expect_str",
    (
        (("scope1", Scope("scope2")), "scope1 scope2"),
        (("scope1", MutableScope("scope2")), "scope1 scope2"),
        ((Scope("scope1"), MutableScope("scope2")), "scope1 scope2"),
        ((Scope("scope1"), MutableScope("scope2"), "scope3"), "scope1 scope2 scope3"),
        (
            ((Scope("scope1"), Scope("scope2")), "scope3 scope4"),
            "scope1 scope2 scope3 scope4",
        ),
        (([[["bar"]]],), "bar"),
    ),
)
def test_scopes_to_str_handles_mixed_data(scope_collection, expect_str):
    assert scopes_to_str(scope_collection) == expect_str


@pytest.mark.parametrize(
    "scope_collection",
    ([Scope("scope1")], Scope("scope1"), "scope1", MutableScope("scope1")),
)
def test_scopes_to_scope_list_simple(scope_collection):
    actual_list = scopes_to_scope_list(scope_collection)

    assert len(actual_list) == 1
    assert isinstance(actual_list[0], Scope)
    assert str(actual_list[0]) == "scope1"


@pytest.mark.parametrize(
    "scope_collection, expect_str",
    (
        (("scope1", "scope2"), "scope1 scope2"),
        (("scope1", MutableScope("scope2")), "scope1 scope2"),
        ((Scope("scope1"), MutableScope("scope2")), "scope1 scope2"),
        ((Scope("scope1"), MutableScope("scope2"), "scope3"), "scope1 scope2 scope3"),
        (
            ((Scope("scope1"), Scope("scope2")), "scope3 scope4"),
            "scope1 scope2 scope3 scope4",
        ),
        (([[["bar"]]],), "bar"),
    ),
)
def test_scopes_to_scope_list_handles_mixed_data(scope_collection, expect_str):
    actual_list = scopes_to_scope_list(scope_collection)

    assert all(isinstance(scope, Scope) for scope in actual_list)
    assert _as_sorted_string(actual_list) == expect_str


def test_scopes_to_scope_list_handles_dependent_scopes():
    scope_collection = "scope1 scope2[scope3 scope4]"
    actual_list = scopes_to_scope_list(scope_collection)

    actual_sorted_str = _as_sorted_string(actual_list)
    # Dependent scope ordering is not guaranteed
    assert (
        actual_sorted_str == "scope1 scope2[scope3 scope4]"
        or actual_sorted_str == "scope1 scope2[scope4 scope3]"
    )


def _as_sorted_string(scope_list) -> str:
    return " ".join(sorted(str(scope) for scope in scope_list))
