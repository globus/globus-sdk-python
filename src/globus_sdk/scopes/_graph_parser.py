from __future__ import annotations

import dataclasses
import sys
import typing as t
from collections import defaultdict, deque

from .errors import ScopeCycleError, ScopeParseError

SPECIAL_CHARACTERS = set("[]* ")
SPECIAL_TOKENS = set("[]*")


class ScopeGraph:
    def __init__(self) -> None:
        self.top_level_scopes: set[tuple[str, bool]] = set()
        self.nodes: set[str] = set()
        self.edges: set[tuple[str, str, bool]] = set()
        self.adjacency_matrix: dict[str, set[tuple[str, str, bool]]] = defaultdict(set)

    def breadth_first_walk(self) -> t.Iterator[tuple[str, bool]]:
        """
        Do a BFS across the forest, returning nodes (as tuples) in BFS order.

        For inspection of the graph after parsing.
        """
        bfs_queue: t.Deque[tuple[str, bool]] = deque(self.top_level_scopes)

        while bfs_queue:
            yield (current := bfs_queue.popleft())

            edges = self.adjacency_matrix[current[0]]
            for _, dest, optional in edges:
                bfs_queue.append((dest, optional))

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

    @classmethod
    def parse(cls, scopes: str) -> ScopeGraph:
        trees = ScopeTreeNode.parse(scopes)
        graph = cls._convert_trees(trees)
        graph._normalize_optionals()
        graph._check_cycles()
        return graph

    @classmethod
    def _convert_trees(cls, trees: list[ScopeTreeNode]) -> ScopeGraph:
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


# pass slots=True on 3.10+
# it's not strictly necessary, but it improves performance
if sys.version_info >= (3, 10):
    _add_dataclass_kwargs: dict[str, bool] = {"slots": True}
else:
    _add_dataclass_kwargs: dict[str, bool] = {}


@dataclasses.dataclass(**_add_dataclass_kwargs)
class ScopeTreeNode:
    #
    # This is an intermediate representation for scope parsing.
    #
    scope_string: str
    optional: bool
    dependencies: list[ScopeTreeNode] = dataclasses.field(default_factory=list)

    def add_dependency(self, subtree: ScopeTreeNode) -> None:
        self.dependencies.append(subtree)

    @staticmethod
    def parse(scope_string: str) -> list[ScopeTreeNode]:
        tokens = _tokenize(scope_string)
        return _parse_tokens(tokens)


def _tokenize(scope_string: str) -> list[str]:
    tokens: list[str] = []
    start = 0
    for idx, current_char, next_char in _peek_enumerate(scope_string):
        if current_char not in SPECIAL_CHARACTERS:
            continue
        _reject_bad_adjacent_characters(current_char, next_char)

        if start != idx:
            tokens.append(scope_string[start:idx])
        start = idx + 1

        if current_char in SPECIAL_TOKENS:
            tokens.append(current_char)
        elif current_char == " ":
            pass
        else:
            raise NotImplementedError
    remainder = scope_string[start:].strip()
    if remainder:
        tokens.append(remainder)
    return tokens


def _reject_bad_adjacent_characters(current_char: str, next_char: str | None) -> None:
    """Given a pair of adjacent characters during tokenization, raise
    appropriate errors if they are not valid."""
    if next_char is None:
        return

    if (current_char, next_char) == ("*", " "):
        raise ScopeParseError("'*' must not be followed by a space")
    elif current_char == "]" and next_char not in (" ", "]"):
        raise ScopeParseError("']' may only be followed by a space or ']'")
    elif (current_char, next_char) == (" ", "["):
        raise ScopeParseError("'[' cannot have a preceding space")


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

    for _, token, next_token in _peek_enumerate(tokens):
        _reject_bad_adjacent_tokens(token, next_token)

        if token == "*":
            current_optional = True
        elif token == "[":
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


def _reject_bad_adjacent_tokens(current_token: str, next_token: str | None) -> None:
    """
    Given a pair of tokens from parsing, raise appropriate errors if they are
    not a valid sequence.
    """
    if current_token == "*":
        if next_token is None:
            raise ScopeParseError("ended in optional marker")
        elif next_token in SPECIAL_TOKENS:
            raise ScopeParseError(
                "a scope string must always follow an optional marker"
            )
    elif (current_token, next_token) == ("[", None):
        raise ScopeParseError("ended in left bracket")
    elif (current_token, next_token) == ("[", "]"):
        raise ScopeParseError("found empty brackets")
    elif (current_token, next_token) == ("[", "["):
        raise ScopeParseError("found double left-bracket")


def _peek_enumerate(data: str | list[str]) -> t.Iterator[tuple[int, str, str | None]]:
    """
    An iterator producing (index, character, next_char)
    or else producing (index, str, next_str)

    (Depending on whether or not the input is a string or list of strings)
    """
    if not data:
        return

    prev: str = data[0]
    for idx, c in enumerate(data[1:]):
        yield (idx, prev, c)
        prev = c

    yield (len(data) - 1, prev, None)
