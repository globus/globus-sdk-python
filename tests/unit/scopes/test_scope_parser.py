import time

import pytest

from globus_sdk import Scope, ScopeCycleError, ScopeParseError


def test_scope_str_and_repr_simple():
    s = Scope("simple")
    assert str(s) == "simple"
    assert repr(s) == "Scope('simple')"


def test_scope_str_and_repr_optional():
    s = Scope("simple", optional=True)
    assert str(s) == "*simple"
    assert repr(s) == "Scope('simple', optional=True)"


def test_scope_str_and_repr_with_dependencies():
    s = Scope("top")
    s.add_dependency("foo")
    assert str(s) == "top[foo]"
    s.add_dependency("bar")
    assert str(s) == "top[foo bar]"
    assert repr(s) == "Scope('top', dependencies=[Scope('foo'), Scope('bar')])"


def test_add_dependency_warns_on_optional_but_still_has_good_str_and_repr():
    s = Scope("top")
    # this should warn, the use of `optional=...` rather than adding a Scope object
    # when optional dependencies are wanted is deprecated
    with pytest.warns(DeprecationWarning):
        s.add_dependency("foo", optional=True)

    # confirm the str representation and repr for good measure
    assert str(s) == "top[*foo]"
    assert repr(s) == "Scope('top', dependencies=[Scope('foo', optional=True)])"


@pytest.mark.parametrize("optional_arg", (True, False))
def test_add_dependency_fails_if_optional_is_combined_with_scope(optional_arg):
    s = Scope("top")
    s2 = Scope("bottom")
    with pytest.raises(ValueError):
        s.add_dependency(s2, optional=optional_arg)


def test_scope_str_nested():
    top = Scope("top")
    mid = Scope("mid")
    bottom = Scope("bottom")
    mid.add_dependency(bottom)
    top.add_dependency(mid)
    assert str(bottom) == "bottom"
    assert str(mid) == "mid[bottom]"
    assert str(top) == "top[mid[bottom]]"


def test_add_dependency_parses_scope_with_optional_marker():
    s = Scope("top")
    s.add_dependency("*subscope")
    assert str(s) == "top[*subscope]"
    assert repr(s) == "Scope('top', dependencies=[Scope('subscope', optional=True)])"


def test_scope_parsing_allows_empty_string():
    scopes = Scope.parse("")
    assert scopes == []


@pytest.mark.parametrize(
    "scope_string1,scope_string2",
    [
        ("foo ", "foo"),
        (" foo", "foo"),
        ("foo[ bar]", "foo[bar]"),
    ],
)
def test_scope_parsing_ignores_non_semantic_whitespace(scope_string1, scope_string2):
    list1 = Scope.parse(scope_string1)
    list2 = Scope.parse(scope_string2)
    assert len(list1) == len(list2) == 1
    s1, s2 = list1[0], list2[0]
    # Scope.__eq__ is not defined, so equivalence checking is manual (and somewhat error
    # prone) for now
    assert s1.scope_string == s2.scope_string
    assert s1.optional == s2.optional
    for i in range(len(s1.dependencies)):
        assert s1.dependencies[i].scope_string == s2.dependencies[i].scope_string
        assert s1.dependencies[i].optional == s2.dependencies[i].optional


@pytest.mark.parametrize(
    "scopestring",
    [
        # ending in '*'
        "foo*",
        "foo *",
        # '*' followed by '[] '
        "foo*[bar]",
        "foo *[bar]",
        "foo [bar*]",
        "foo * ",
        "* foo",
        # empty brackets
        "foo[]",
        # starting with open bracket
        "[foo]",
        # double brackets
        "foo[[bar]]",
        # unbalanced open brackets
        "foo[",
        "foo[bar",
        # unbalanced close brackets
        "foo]",
        "foo bar]",
        "foo[bar]]",
        "foo[bar] baz]",
        # space before brackets
        "foo [bar]",
        # missing space before next scope string after ']'
        "foo[bar]baz",
    ],
)
def test_scope_parsing_rejects_bad_inputs(scopestring):
    with pytest.raises(ScopeParseError):
        Scope.parse(scopestring)


@pytest.mark.parametrize(
    "scopestring",
    [
        "foo[foo]",
        "foo[*foo]",
        "foo[bar[foo]]",
        "foo[bar[baz[bar]]]",
        "foo[bar[*baz[bar]]]",
        "foo[bar[*baz[*bar]]]",
    ],
)
def test_scope_parsing_catches_and_rejects_cycles(scopestring):
    with pytest.raises(ScopeCycleError):
        Scope.parse(scopestring)


@pytest.mark.flaky
def test_scope_parsing_catches_and_rejects_very_large_cycles_quickly():
    """
    WARNING: this test is hardware speed dependent and could fail on slow systems.

    This test creates a very long cycle and validates that it can be caught in a
    small timeframe of < 100ms.
    Observed times on a test system were <20ms, and in CI were <60ms.

    Although checking the speed in this way is not ideal, we want to avoid high
    time-complexity in the cycle detection. This test offers good protection against any
    major performance regression.
    """
    scope_string = ""
    for i in range(1000):
        scope_string += f"foo{i}["
    scope_string += " foo10"
    for _ in range(1000):
        scope_string += "]"

    t0 = time.time()
    with pytest.raises(ScopeCycleError):
        Scope.parse(scope_string)
    t1 = time.time()
    assert t1 - t0 < 0.1


@pytest.mark.parametrize(
    "scopestring",
    ("foo", "*foo", "foo[bar]", "foo[*bar]", "foo bar", "foo[bar[baz]]"),
)
def test_scope_parsing_accepts_valid_inputs(scopestring):
    # test *only* that parsing does not error and returns a non-empty list of scopes
    scopes = Scope.parse(scopestring)
    assert isinstance(scopes, list)
    assert len(scopes) > 0
    assert isinstance(scopes[0], Scope)


def test_scope_deserialize_simple():
    scope = Scope.deserialize("foo")
    assert str(scope) == "foo"


def test_scope_deserialize_with_dependencies():
    # oh, while we're here, let's also check that our whitespace insensitivity works
    scope = Scope.deserialize("foo[ bar   *baz  ]")
    assert str(scope) in ("foo[bar *baz]", "foo[*baz bar]")


def test_scope_deserialize_fails_on_empty():
    with pytest.raises(ValueError):
        Scope.deserialize("  ")


def test_scope_deserialize_fails_on_multiple_top_level_scopes():
    with pytest.raises(ValueError):
        Scope.deserialize("foo bar")


@pytest.mark.parametrize("scope_str", ("*foo", "foo[bar]", "foo[", "foo]", "foo bar"))
def test_scope_init_forbids_special_chars(scope_str):
    with pytest.raises(ValueError):
        Scope(scope_str)


@pytest.mark.parametrize(
    "original, reserialized",
    [
        ("foo[bar *bar]", {"foo[bar]"}),
        ("foo[*bar bar]", {"foo[bar]"}),
        ("foo[bar[baz]] bar[*baz]", {"foo[bar[baz]]", "bar[baz]"}),
        ("foo[bar[*baz]] bar[baz]", {"foo[bar[baz]]", "bar[baz]"}),
    ],
)
def test_scope_parsing_normalizes_optionals(original, reserialized):
    assert {s.serialize() for s in Scope.parse(original)} == reserialized
