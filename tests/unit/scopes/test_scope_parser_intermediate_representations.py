from globus_sdk.scopes._graph_parser import ScopeGraph, ScopeTreeNode


def test_graph_str_single_node():
    g = ScopeGraph.parse("foo")
    clean_str = _blank_lines_removed(str(g))
    assert (
        clean_str
        == """\
digraph scopes {
  rankdir="LR";
  foo
}"""
    )


def test_graph_str_single_optional_node():
    g = ScopeGraph.parse("*foo")
    clean_str = _blank_lines_removed(str(g))
    assert (
        clean_str
        == """\
digraph scopes {
  rankdir="LR";
  *foo
}"""
    )


def test_graph_str_single_dependency():
    g = ScopeGraph.parse("foo[bar]")
    clean_str = _blank_lines_removed(str(g))
    assert (
        clean_str
        == """\
digraph scopes {
  rankdir="LR";
  foo
  foo -> bar;
}"""
    )


def test_graph_str_optional_dependency():
    g = ScopeGraph.parse("foo[bar[*baz]]")
    clean_str = _blank_lines_removed(str(g))
    assert (
        clean_str
        == """\
digraph scopes {
  rankdir="LR";
  foo
  foo -> bar;
  bar -> baz [ label = "optional" ];
}"""
    )


def test_treenode_repr():
    t = ScopeTreeNode("foo", optional=False)
    assert repr(t) == "ScopeTreeNode('foo')"

    t = ScopeTreeNode("foo", optional=True)
    assert repr(t) == "ScopeTreeNode('foo', optional=True)"

    t = ScopeTreeNode("foo", optional=False)
    t.dependencies = [ScopeTreeNode("bar", optional=False)]
    assert repr(t) == "ScopeTreeNode('foo', dependencies=[ScopeTreeNode('bar')])"


def _blank_lines_removed(s: str) -> str:
    return "\n".join(line for line in s.split("\n") if line.strip() != "")
