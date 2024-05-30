from globus_sdk.scopes import Scope


def test_base_scope_strings():
    s1 = [Scope("foo"), Scope("bar")]
    s2 = [Scope("foo"), Scope("baz")]
    merged = Scope.merge_scopes(s1, s2)
    assert [s.serialize() for s in merged] == ["foo", "bar", "baz"]


def test_all_optional_dependencies():
    s1 = [Scope("foo", optional=True)]
    s2 = [Scope("foo", optional=True)]
    merged = Scope.merge_scopes(s1, s2)
    assert [s.serialize() for s in merged] == ["*foo"]


def test_mixed_optional_dependencies():
    s1 = [Scope("foo", optional=True)]
    s2 = [Scope("foo", optional=False)]
    merged = Scope.merge_scopes(s1, s2)
    assert [s.serialize() for s in merged] == ["foo"]


def test_different_dependencies():
    s1 = [Scope("foo").add_dependency("bar")]
    s2 = [Scope("foo").add_dependency("baz")]
    merged = Scope.merge_scopes(s1, s2)
    assert [s.serialize() for s in merged] == ["foo[bar baz]"]


def test_optional_dependencies():
    s1 = [Scope("foo").add_dependency("bar")]
    s2 = [Scope("foo").add_dependency("*bar")]
    merged = Scope.merge_scopes(s1, s2)
    assert [s.serialize() for s in merged] == ["foo[bar]"]


def test_multi_level_dependencies():
    s1 = [Scope("foo").add_dependency(Scope("bar").add_dependency("baz"))]
    s2 = [Scope("foo").add_dependency(Scope("baz").add_dependency("bar"))]
    merged = Scope.merge_scopes(s1, s2)
    assert [s.serialize() for s in merged] == ["foo[bar[baz] baz[bar]]"]
