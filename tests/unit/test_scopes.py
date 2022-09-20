import uuid

import pytest

from globus_sdk.scopes import FlowsScopes, MutableScope, ScopeBuilder


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


def test_mutable_scope_str_and_repr_simple():
    s = MutableScope("simple")
    assert str(s) == "simple"
    assert repr(s) == "MutableScope('simple')"

    s2 = MutableScope("simple", optional=True)
    assert str(s2) == "*simple"
    assert repr(s2) == "MutableScope('simple', optional=True)"


def test_mutable_scope_str_and_repr_with_dependencies():
    s = MutableScope("top")
    s.add_dependency("foo")
    assert str(s) == "top[foo]"
    s.add_dependency("bar", optional=True)
    # NOTE: order is not guaranteed for dict() until python3.7
    assert str(s) in ("top[foo *bar]", "top[*bar foo]")
    assert repr(s) in (
        "MutableScope('top', dependencies={'foo': False, 'bar': True})",
        "MutableScope('top', dependencies={'bar': True, 'foo': False})",
    )

    s2 = MutableScope("top", optional=True)
    s2.add_dependency("foo")
    assert str(s2) == "*top[foo]"
    s2.add_dependency("bar", optional=True)
    # NOTE: order is not guaranteed for dict() until python3.7
    assert str(s2) in ("*top[foo *bar]", "*top[*bar foo]")
    assert repr(s2) in (
        "MutableScope('top', optional=True, dependencies={'foo': False, 'bar': True})",
        "MutableScope('top', optional=True, dependencies={'bar': True, 'foo': False})",
    )


def test_mutable_scope_str_nested():
    top = MutableScope("top")
    mid = MutableScope("mid")
    bottom = MutableScope("bottom")
    mid.add_dependency(str(bottom))
    top.add_dependency(str(mid))
    assert str(bottom) == "bottom"
    assert str(mid) == "mid[bottom]"
    assert str(top) == "top[mid[bottom]]"


def test_mutable_scope_collection_to_str():
    foo = MutableScope("foo")
    bar = MutableScope("bar")
    baz = "baz"
    assert MutableScope.scopes2str(foo) == "foo"
    assert MutableScope.scopes2str([foo, bar]) == "foo bar"
    assert MutableScope.scopes2str(baz) == "baz"
    assert MutableScope.scopes2str([foo, baz]) == "foo baz"


def test_mutable_scope_rejects_scope_with_optional_marker():
    s = MutableScope("top")
    with pytest.raises(ValueError) as excinfo:
        s.add_dependency("*subscope")

    assert "add_dependency cannot contain a leading '*'" in str(excinfo.value)


def test_scopebuilder_make_mutable_produces_same_strings():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_scopes="foo", known_url_scopes="bar")
    assert str(sb.make_mutable("foo")) == sb.foo
    assert str(sb.make_mutable("bar")) == sb.bar


def test_flows_scopes_creation():
    assert FlowsScopes.resource_server == "flows.globus.org"
    assert (
        FlowsScopes.run
        == "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run"
    )
