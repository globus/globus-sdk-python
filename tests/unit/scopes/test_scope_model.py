import uuid

from globus_sdk.scopes import Scope


def test_scope_with_dependency_leaves_original_unchanged():
    s1 = Scope(uuid.uuid1().hex)
    s2 = Scope("s2")
    s3 = s1.with_dependency(s2)

    assert s1.scope_string == s3.scope_string
    assert len(s1.dependencies) == 0
    assert len(s3.dependencies) == 1


def test_scope_with_dependencies_leaves_original_unchanged():
    s1 = Scope(uuid.uuid1().hex)
    s2 = Scope("s2")
    s3 = Scope("s3")
    s4 = s1.with_dependencies((s2, s3))

    assert s1.scope_string == s4.scope_string
    assert len(s1.dependencies) == 0
    assert len(s4.dependencies) == 2


def test_scope_with_optional_leaves_original_unchanged():
    s1 = Scope(uuid.uuid1().hex)
    s2 = s1.with_optional(True)
    s3 = s2.with_optional(False)

    assert s1.scope_string == s2.scope_string == s3.scope_string
    assert len(s1.dependencies) == 0
    assert len(s2.dependencies) == 0
    assert len(s3.dependencies) == 0

    assert not s1.optional
    assert s2.optional
    assert not s3.optional
