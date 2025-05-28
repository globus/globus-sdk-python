import uuid

from globus_sdk.scopes import ComputeScopes, FlowsScopes, ScopeBuilder


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


def test_flows_scopes_creation():
    assert FlowsScopes.resource_server == "flows.globus.org"
    assert (
        FlowsScopes.run
        == "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run"
    )


def test_compute_scopes_creation():
    assert ComputeScopes.resource_server == "funcx_service"
    assert (
        ComputeScopes.all
        == "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all"
    )


def test_stringify_scope_builder():
    class MyScopeBuilder(ScopeBuilder):
        pass

    sb = MyScopeBuilder("foo", known_scopes=["sc1"])
    assert (
        str(sb)
        == """\
MyScopeBuilder[foo]
  sc1:
    urn:globus:auth:scope:foo:sc1"""
    )
