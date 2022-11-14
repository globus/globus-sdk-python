import uuid

import pytest

from globus_sdk.scopes import FlowsScopes, Scope, ScopeBuilder, ScopeParseError


def test_url_scope_string():
    sb = ScopeBuilder(str(uuid.UUID(int=0)))
    assert sb.url_scope_string("data_access") == (
        "https://auth.globus.org/scopes/00000000-0000-0000-0000-000000000000"
        "/data_access"
    )


def test_urn_scope_string():
    sb = ScopeBuilder("example.globus.org")
    assert (
        sb.urn_scope_string("scope") == "urn:globus:auth:scope:example.globus.org:scope"
    )


def test_known_scopes():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_scopes="foo")
    assert sb.foo == "urn:globus:auth:scope:00000000-0000-0000-0000-000000000000:foo"


def test_known_url_scopes():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_url_scopes="foo")
    assert sb.foo == (
        "https://auth.globus.org/scopes/00000000-0000-0000-0000-000000000000/foo"
    )


def test_scopebuilder_str():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_scopes="foo", known_url_scopes="bar")
    rs, foo_scope, bar_scope = sb.resource_server, sb.foo, sb.bar

    stringified = str(sb)
    assert rs in stringified
    assert foo_scope in stringified
    assert bar_scope in stringified


def test_uniquely_named_scopes():
    rs = str(uuid.uuid4())
    scope_1 = str(uuid.uuid4())
    scope_2 = str(uuid.uuid4())
    sb = ScopeBuilder(
        rs,
        known_scopes=[("my_urn_scope", scope_1), "foo"],
        known_url_scopes=[("my_url_scope", scope_2), "bar"],
    )

    assert sb.my_urn_scope == f"urn:globus:auth:scope:{rs}:{scope_1}"
    assert sb.foo == f"urn:globus:auth:scope:{rs}:foo"
    assert sb.my_url_scope == f"https://auth.globus.org/scopes/{rs}/{scope_2}"
    assert sb.bar == f"https://auth.globus.org/scopes/{rs}/bar"


def test_sb_allowed_inputs_types():
    rs = str(uuid.uuid4())
    scope_1 = "do_a_thing"
    scope_1_urn = f"urn:globus:auth:scope:{rs}:{scope_1}"

    none_sb = ScopeBuilder(rs, known_scopes=None)
    str_sb = ScopeBuilder(rs, known_scopes=scope_1)
    tuple_sb = ScopeBuilder(rs, known_scopes=("scope_1", scope_1))
    list_sb = ScopeBuilder(rs, known_scopes=[scope_1, ("scope_1", scope_1)])

    assert none_sb.scope_names == []
    assert scope_1 in str_sb.scope_names
    assert str_sb.do_a_thing == scope_1_urn
    assert "scope_1" in tuple_sb.scope_names
    assert tuple_sb.scope_1 == scope_1_urn
    assert scope_1 in list_sb.scope_names
    assert "scope_1" in list_sb.scope_names
    assert list_sb.scope_1 == scope_1_urn
    assert list_sb.do_a_thing == scope_1_urn


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


def test_scope_collection_to_str():
    foo = Scope("foo")
    bar = Scope("bar")
    baz = "baz"
    assert Scope.scopes2str(foo) == "foo"
    assert Scope.scopes2str([foo, bar]) == "foo bar"
    assert Scope.scopes2str(baz) == "baz"
    assert Scope.scopes2str([foo, baz]) == "foo baz"


def test_add_dependency_parses_scope_with_optional_marker():
    s = Scope("top")
    s.add_dependency("*subscope")
    assert str(s) == "top[*subscope]"
    assert repr(s) == "Scope('top', dependencies=[Scope('subscope', optional=True)])"


def test_scopebuilder_make_mutable_produces_same_strings():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_scopes="foo", known_url_scopes="bar")
    assert str(sb.make_mutable("foo")) == sb.foo
    assert str(sb.make_mutable("bar")) == sb.bar


def test_scopebuilder_make_mutable_can_be_optional():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_scopes="foo")
    assert str(sb.make_mutable("foo", optional=True)) == "*" + sb.foo


def test_flows_scopes_creation():
    assert FlowsScopes.resource_server == "flows.globus.org"
    assert (
        FlowsScopes.run
        == "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run"
    )


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
    assert s1._scope_string == s2._scope_string
    assert s1.optional == s2.optional
    for i in range(len(s1.dependencies)):
        assert s1.dependencies[i]._scope_string == s2.dependencies[i]._scope_string
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
    ("foo", "*foo", "foo[bar]", "foo[*bar]", "foo bar", "foo[bar[baz]]"),
)
def test_scope_parsing_accepts_valid_inputs(scopestring):
    # test *only* that parsing does not error and returns a non-empty list of scopes
    scopes = Scope.parse(scopestring)
    assert isinstance(scopes, list)
    assert len(scopes) > 0
    assert isinstance(scopes[0], Scope)


@pytest.mark.parametrize("rs_name", (str(uuid.UUID(int=0)), "example.globus.org"))
@pytest.mark.parametrize("scope_format", ("urn", "url"))
def test_scope_parsing_can_consume_scopebuilder_results(rs_name, scope_format):
    sb = ScopeBuilder(rs_name)
    if scope_format == "urn":
        scope_string = sb.urn_scope_string("foo")
        expect_string = f"urn:globus:auth:scope:{rs_name}:foo"
    elif scope_format == "url":
        scope_string = sb.url_scope_string("foo")
        expect_string = f"https://auth.globus.org/scopes/{rs_name}/foo"
    else:
        raise NotImplementedError

    scope = Scope.deserialize(scope_string)
    assert str(scope) == expect_string


def test_scope_deserialize_simple():
    scope = Scope.deserialize("foo")
    assert str(scope) == "foo"


def test_scope_deserialize_with_dependencies():
    # oh, while we're here, let's also check that our whitespace insensitivity works
    scope = Scope.deserialize("foo[ bar   *baz  ]")
    assert str(scope) == "foo[bar *baz]"


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


def test_scope_contains_requires_scope_objects():
    s = Scope("foo")
    assert not s._contains("foo")


@pytest.mark.parametrize(
    "contained, containing, expect",
    [
        # string matching, including optional on both sides
        ("foo", "foo", True),  # identity
        ("*foo", "*foo", True),  # identity
        ("foo", "bar", False),
        ("foo", "*bar", False),
        ("*foo", "bar", False),
        # optional-ness is one-way when mismatched
        ("foo", "*foo", False),
        ("*foo", "foo", True),
        # dependency matching is also one-way when mismatched
        ("foo[bar]", "foo[bar]", True),  # identity
        ("foo[bar]", "foo", False),
        ("foo", "foo[bar]", True),
        ("foo", "foo[bar[baz]]", True),
        ("foo[bar]", "foo[bar[baz]]", True),
        ("foo[bar[baz]]", "foo[bar[baz]]", True),  # identity
        # and the combination of dependencies with optional also works
        ("foo[*bar]", "foo[bar[baz]]", True),
        ("foo[*bar]", "foo[*bar[baz]]", True),
        ("foo[bar]", "foo[bar[*baz]]", True),
        ("foo[*bar]", "foo[bar[*baz]]", True),
    ],
)
def test_scope_contains_simple_cases(contained, containing, expect):
    outer_s = Scope.deserialize(containing)
    inner_s = Scope.deserialize(contained)
    assert outer_s._contains(inner_s) == expect


@pytest.mark.parametrize(
    "contained, containing, expect",
    [
        # "simple" cases for multiple dependencies
        ("foo[bar baz]", "foo[bar[baz] baz]", True),
        ("foo[bar baz]", "foo[bar[baz]]", False),
        ("foo[baz bar]", "foo[bar[baz] baz]", True),
        ("foo[bar baz]", "foo[bar[baz] baz buzz]", True),
        # these scenarios will mirror some "realistic" usage
        (
            "timer[transfer_ap[transfer]]",
            "timer[transfer_ap[transfer[*foo/data_access]]]",
            True,
        ),
        (
            "timer[transfer_ap[transfer[*foo/data_access]]]",
            "timer[transfer_ap[transfer[*foo/data_access *bar/data_access]]]",
            True,
        ),
        (
            "timer[transfer_ap[transfer[*bar *foo]]]",
            "timer[transfer_ap[transfer[*foo *bar *baz]]]",
            True,
        ),
        (
            "timer[transfer_ap[transfer[*foo/data_access]]]",
            "timer[transfer_ap[transfer]]",
            False,
        ),
        (
            "timer[transfer_ap[transfer[*foo/data_access *bar/data_access]]]",
            "timer[transfer_ap[transfer[*foo/data_access]]]",
            False,
        ),
        (
            "timer[transfer_ap[transfer[foo/data_access]]]",
            "timer[transfer_ap[transfer[*foo/data_access]]]",
            False,
        ),
        (
            "timer[transfer_ap[transfer[*foo/data_access]]]",
            "timer[transfer_ap[transfer[foo/data_access]]]",
            True,
        ),
        (
            "timer[transfer_ap[*transfer[*foo/data_access]]]",
            "timer[transfer_ap[transfer[foo/data_access]]]",
            True,
        ),
        (
            "timer[transfer_ap[transfer[*foo/data_access]]]",
            "timer[transfer_ap[*transfer[foo/data_access]]]",
            False,
        ),
    ],
)
def test_scope_contains_complex_usages(contained, containing, expect):
    outer_s = Scope.deserialize(containing)
    inner_s = Scope.deserialize(contained)
    assert outer_s._contains(inner_s) == expect
