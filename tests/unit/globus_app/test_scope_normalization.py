import pytest

import globus_sdk
from globus_sdk.scopes import Scope


@pytest.fixture
def user_app():
    client_id = "mock_client_id"
    return globus_sdk.UserApp("test-app", client_id=client_id)


@pytest.mark.parametrize(
    "scope_collection",
    ([Scope("scope1")], Scope("scope1"), "scope1", ["scope1"]),
)
def test_iter_scopes_simple(user_app, scope_collection):
    actual_list = list(user_app._iter_scopes(scope_collection))

    assert len(actual_list) == 1
    assert isinstance(actual_list[0], Scope)
    assert str(actual_list[0]) == "scope1"


@pytest.mark.parametrize(
    "scope_collection, expect_str",
    (
        (("scope1", "scope2"), "scope1 scope2"),
        (("scope1", Scope("scope2")), "scope1 scope2"),
        ((Scope("scope1"), Scope("scope2")), "scope1 scope2"),
        ((Scope("scope1"), Scope("scope2"), "scope3"), "scope1 scope2 scope3"),
        (
            (Scope("scope1"), Scope("scope2"), "scope3 scope4"),
            "scope1 scope2 scope3 scope4",
        ),
        ([Scope("scope1"), "scope2", "scope3 scope4"], "scope1 scope2 scope3 scope4"),
    ),
)
def test_iter_scopes_handles_mixed_data(user_app, scope_collection, expect_str):
    actual_list = list(user_app._iter_scopes(scope_collection))

    assert all(isinstance(scope, Scope) for scope in actual_list)
    assert _as_sorted_string(actual_list) == expect_str


def test_iter_scopes_handles_dependent_scopes(user_app):
    scope_collection = "scope1 scope2[scope3 scope4]"
    actual_list = list(user_app._iter_scopes(scope_collection))

    actual_sorted_str = _as_sorted_string(actual_list)
    # Dependent scope ordering is not guaranteed
    assert (
        actual_sorted_str == "scope1 scope2[scope3 scope4]"
        or actual_sorted_str == "scope1 scope2[scope4 scope3]"
    )


def _as_sorted_string(scope_list) -> str:
    return " ".join(sorted(str(scope) for scope in scope_list))
