import pytest

from globus_sdk.scopes import MutableScope


def test_scope_str_and_repr_simple():
    s = MutableScope("simple")
    assert str(s) == "simple"
    assert repr(s) == "MutableScope('simple')"


def test_scope_str_and_repr_optional():
    s = MutableScope("simple", optional=True)
    assert str(s) == "*simple"
    assert repr(s) == "MutableScope('simple', optional=True)"


def test_scope_str_and_repr_with_dependencies():
    s = MutableScope("top")
    s.add_dependency("foo")
    assert str(s) == "top[foo]"
    s.add_dependency("bar")
    assert str(s) == "top[foo bar]"
    assert (
        repr(s) == "MutableScope('top', "
        "dependencies=[MutableScope('foo'), MutableScope('bar')])"
    )


def test_add_dependency_warns_on_optional_but_still_has_good_str_and_repr():
    s = MutableScope("top")
    # this should warn, the use of `optional=...` rather than adding a Scope object
    # when optional dependencies are wanted is deprecated
    with pytest.warns(DeprecationWarning):
        s.add_dependency("foo", optional=True)

    # confirm the str representation and repr for good measure
    assert str(s) == "top[*foo]"
    assert (
        repr(s)
        == "MutableScope('top', dependencies=[MutableScope('foo', optional=True)])"
    )


@pytest.mark.parametrize("scope_str", ("*foo", "foo[bar]", "foo[", "foo]", "foo bar"))
def test_scope_init_forbids_special_chars(scope_str):
    with pytest.raises(ValueError):
        MutableScope(scope_str)
