from globus_sdk.scopes import Scope


def test_base_scope_strings():
    s1 = [Scope("foo"), Scope("bar")]
    s2 = [Scope("foo"), Scope("baz")]
    merged = Scope.merge_scopes(s1, s2)
    assert len(merged) == 3

    str_list = [s.serialize() for s in merged]
    assert "foo" in str_list
    assert "bar" in str_list
    assert "baz" in str_list


def test_mixed_optional_dependencies():
    s1 = [Scope("foo", optional=True)]
    s2 = [Scope("foo", optional=False)]
    merged = Scope.merge_scopes(s1, s2)
    assert len(merged) == 2

    str_list = [s.serialize() for s in merged]
    assert "foo" in str_list
    assert "*foo" in str_list


def test_different_dependencies():
    s1 = [Scope("foo").add_dependency("bar")]
    s2 = [Scope("foo").add_dependency("baz")]
    merged = Scope.merge_scopes(s1, s2)
    assert len(merged) == 1
    assert merged[0].scope_string == "foo"

    dependency_str_list = [s.serialize() for s in merged[0].dependencies]
    assert len(dependency_str_list) == 2
    assert "bar" in dependency_str_list
    assert "baz" in dependency_str_list


def test_optional_dependencies():
    s1 = [Scope("foo").add_dependency("bar")]
    s2 = [Scope("foo").add_dependency("*bar")]
    merged = Scope.merge_scopes(s1, s2)
    assert len(merged) == 1
    assert merged[0].scope_string == "foo"

    dependency_str_list = [s.serialize() for s in merged[0].dependencies]
    assert len(dependency_str_list) == 1
    assert "bar" in dependency_str_list


def test_different_dependencies_on_mixed_optional_base():
    s1 = [Scope("foo").add_dependency("bar")]
    s2 = [Scope("foo", optional=True).add_dependency("baz")]
    merged = Scope.merge_scopes(s1, s2)
    assert len(merged) == 2

    for scope in merged:
        dependency_str_list = [s.serialize() for s in scope.dependencies]
        assert len(dependency_str_list) == 2
        assert "bar" in dependency_str_list
        assert "baz" in dependency_str_list
