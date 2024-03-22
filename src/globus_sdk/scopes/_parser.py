from __future__ import annotations

import typing as t
from collections import defaultdict, deque

from .errors import ScopeCycleError, ScopeParseError

SPECIAL_CHARACTERS = set("[]* ")
SPECIAL_TOKENS = set("[]*")


def _tokenize(scope_string: str) -> list[str]:
    tokens: list[str] = []
    start = 0
    for idx, c in enumerate(scope_string):
        try:
            peek: str | None = scope_string[idx + 1]
        except IndexError:
            peek = None

        if c in SPECIAL_CHARACTERS:
            if start != idx:
                tokens.append(scope_string[start:idx])

            start = idx + 1
            if c == "*":
                if peek == " ":
                    raise ScopeParseError("'*' must not be followed by a space")
                tokens.append(c)
            elif c == "[":
                tokens.append(c)
            elif c == "]":
                if peek is not None and peek not in (" ", "]"):
                    raise ScopeParseError("']' may only be followed by a space or ']'")
                tokens.append(c)
            elif c == " ":
                if peek == "[":
                    raise ScopeParseError("'[' cannot have a preceding space")
            else:
                raise NotImplementedError
    remainder = scope_string[start:].strip()
    if remainder:
        tokens.append(remainder)
    return tokens


def _parse_tokens(tokens: list[str]) -> list[ScopeTreeNode]:
    # value to return
    ret: list[ScopeTreeNode] = []
    # track whether or not the current scope is optional (has a preceding *)
    current_optional = False
    # keep a stack of "parents", each time we enter a `[` context, push the last scope
    # and each time we exit via a `]`, pop from the stack
    parents: list[ScopeTreeNode] = []
    # track the current (or, by similar terminology, "last") complete scope seen
    current_scope: ScopeTreeNode | None = None

    for idx in range(len(tokens)):
        token = tokens[idx]
        try:
            peek: str | None = tokens[idx + 1]
        except IndexError:
            peek = None

        if token == "*":
            current_optional = True
            if peek is None:
                raise ScopeParseError("ended in optional marker")
            if peek in SPECIAL_TOKENS:
                raise ScopeParseError(
                    "a scope string must always follow an optional marker"
                )

        elif token == "[":
            if peek is None:
                raise ScopeParseError("ended in left bracket")
            if peek == "]":
                raise ScopeParseError("found empty brackets")
            if peek == "[":
                raise ScopeParseError("found double left-bracket")
            if not current_scope:
                raise ScopeParseError("found '[' without a preceding scope string")

            parents.append(current_scope)
        elif token == "]":
            if not parents:
                raise ScopeParseError("found ']' with no matching '[' preceding it")
            parents.pop()
        else:
            current_scope = ScopeTreeNode(token, optional=current_optional)
            current_optional = False
            if parents:
                parents[-1].add_dependency(current_scope)
            else:
                ret.append(current_scope)
    if parents:
        raise ScopeParseError("unclosed brackets, missing ']'")

    return ret


class ScopeTreeNode:
    #
    # This is an intermediate representation for scope parsing.
    #
    def __init__(
        self,
        scope_string: str,
        *,
        optional: bool,
    ) -> None:
        self.scope_string = scope_string
        self.optional = optional
        self.dependencies: list[ScopeTreeNode] = []

    def add_dependency(self, subtree: ScopeTreeNode) -> None:
        self.dependencies.append(subtree)

    def __repr__(self) -> str:
        parts: list[str] = [f"'{self.scope_string}'"]
        if self.optional:
            parts.append("optional=True")
        if self.dependencies:
            parts.append(f"dependencies={self.dependencies!r}")
        return "ScopeTreeNode(" + ", ".join(parts) + ")"

    @staticmethod
    def parse(scope_string: str) -> list[ScopeTreeNode]:
        tokens = _tokenize(scope_string)
        return _parse_tokens(tokens)


class ScopeGraph:
    def __init__(self) -> None:
        self.top_level_scopes: set[tuple[str, bool]] = set()
        self.nodes: set[str] = set()
        self.edges: set[tuple[str, str, bool]] = set()
        self.adjacency_matrix: dict[str, set[tuple[str, str, bool]]] = defaultdict(set)

    def add_edge(self, src: str, dest: str, optional: bool) -> None:
        self.edges.add((src, dest, optional))
        self.adjacency_matrix[src].add((src, dest, optional))

    def _normalize_optionals(self) -> None:
        to_remove: set[tuple[str, str, bool]] = set()
        for edge in self.edges:
            src, dest, optional = edge
            if not optional:
                continue
            alter_ego = (src, dest, not optional)
            if alter_ego in self.edges:
                to_remove.add(edge)
        self.edges = self.edges - to_remove
        for edge in to_remove:
            src, _, _ = edge
            self.adjacency_matrix[src].remove(edge)

    def _check_cycles(self) -> None:
        # explore the graph using an iterative Depth-First Search
        # as we explore the graph, keep track of paths of ancestry being explored
        # if we ever find a back-edge along one of those paths of ancestry, that
        # means that there must be a cycle

        # start from the top-level nodes (which we know to be the roots of this
        # forest-shaped graph)
        # we will track this as the set of paths to continue to branch and explore in a
        # stack and pop from it until it is empty, thus implementing DFS
        #
        # conceptually, the paths could be implemented as `list[str]`, which would
        # preserve the order in which we encountered each node. Using a set is a
        # micro-optimization which makes checks faster, since we only care to detect
        # *that* there was a cycle, not what the shape of that cycle was
        paths_to_explore: list[tuple[set[str], str]] = [
            ({node}, node) for node, _ in self.top_level_scopes
        ]

        while paths_to_explore:
            path, terminus = paths_to_explore.pop()

            # get out-edges from the last node in the path
            children = self.adjacency_matrix[terminus]

            # if the node was a leaf, no children, we are done exploring this path
            if not children:
                continue

            # for each child edge, do two basic things:
            # - check if we found a back-edge (cycle!)
            # - create a new path to explore, with the child node as its current
            #   terminus
            for edge in children:
                _, dest, _ = edge
                if dest in path:
                    raise ScopeCycleError(f"A cycle was found involving '{dest}'")
                paths_to_explore.append((path.union((dest,)), dest))

    def __str__(self) -> str:
        lines = ["digraph scopes {", '  rankdir="LR";', ""]
        for node, optional in self.top_level_scopes:
            lines.append(f"  {'*' if optional else ''}{node}")
        lines.append("")

        # do two passes to put all non-optional edges first
        for source, dest, optional in self.edges:
            if optional:
                continue
            lines.append(f"  {source} -> {dest};")
        for source, dest, optional in self.edges:
            if not optional:
                continue
            lines.append(f'  {source} -> {dest} [ label = "optional" ];')
        lines.append("")
        lines.append("}")
        return "\n".join(lines)


def _convert_trees(trees: list[ScopeTreeNode]) -> ScopeGraph:
    graph = ScopeGraph()
    node_queue: t.Deque[ScopeTreeNode] = deque()

    for tree_node in trees:
        node_queue.append(tree_node)
        graph.top_level_scopes.add((tree_node.scope_string, tree_node.optional))

    while node_queue:
        tree_node = node_queue.pop()
        scope_string = tree_node.scope_string
        graph.nodes.add(scope_string)
        for dep in tree_node.dependencies:
            node_queue.append(dep)
            graph.add_edge(scope_string, dep.scope_string, dep.optional)

    return graph


def parse_scope_graph(scopes: str) -> ScopeGraph:
    trees = ScopeTreeNode.parse(scopes)
    graph = _convert_trees(trees)
    graph._normalize_optionals()
    graph._check_cycles()
    return graph
