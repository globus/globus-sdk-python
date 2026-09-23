from __future__ import annotations

import dataclasses
import enum
import typing as t
from collections import defaultdict, deque

from .errors import ScopeCycleError, ScopeParseError

SPECIAL_CHARACTERS = set("[]* ")
SPECIAL_TOKENS = set("[]*")


class ScopeGraph:
    def __init__(self) -> None:
        self.top_level_scopes: set[tuple[str, bool]] = set()
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
            # The current edge is optional; see if it's superseded by required edge
            required_variant = (src, dest, False)
            if required_variant in self.edges:
                to_remove.add(edge)
        self.edges = self.edges - to_remove
        for edge in to_remove:
            src, _, _ = edge
            self.adjacency_matrix[src].remove(edge)

    def _check_cycles(self) -> None:
        """
        Check the graph for cycles, and if one is detected immediately error.
        """
        detector = _CycleDetector(self)
        detector.run()

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
            for dep in tree_node.dependencies:
                node_queue.append(dep)
                graph.add_edge(scope_string, dep.scope_string, dep.optional)

        return graph


@dataclasses.dataclass(slots=True)
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


class _DetectorStates(enum.Enum):
    UNVISITED = enum.auto()
    ON_CURRENT_PATH = enum.auto()
    PROVEN_NO_CYCLE = enum.auto()


class _CycleDetector:
    """
    A stateful object which can detect cycles in scope graphs.
    """

    def __init__(self, graph: ScopeGraph) -> None:
        self.graph = graph
        # stack of pairs: (node, out-edge-iterator)
        self.visit_stack: list[tuple[str, t.Iterator[tuple[str, str, bool]]]] = []
        self.node_states: dict[str, _DetectorStates] = {}

    def _start_nodes(self) -> t.Iterator[str]:
        for root, _ in self.graph.top_level_scopes:
            yield root

    def _stack_push(self, node: str) -> None:
        # The use of `iter()` copies the set of edges into a consumable iterator.
        self.visit_stack.append((node, iter(self.graph.adjacency_matrix[node])))

    def run(self) -> None:
        """
        Check the graph for cycles, and if one is detected immediately error.
        """
        # Perform a DFS traversal keeping track of nodes on the current path, looking
        # for any back-edges. (Back-edges are cycles.)
        #
        # If a node has already been explored and proven not to produce cycles, then
        # it is marked as such to save us from needing to do extra traversals.
        #
        # Nodes start out unvisited, in that they are not in the visited node tracking.
        for start in self._start_nodes():
            # If we already proved this node out, because one root refers to another,
            # don't do any extra work.
            if self.node_states.get(start) is _DetectorStates.PROVEN_NO_CYCLE:
                continue

            # Now a traversal begins, starting from this root node.
            self.node_states[start] = _DetectorStates.ON_CURRENT_PATH

            self._stack_push(start)
            while self.visit_stack:
                # Peek at the top of the stack, but do not pop. We may be descending,
                # and we want to be able to later resume exploration of the graph at
                # this node.
                current_node, edges = self.visit_stack[-1]

                # walk all of the out-edges
                for _, dest, _ in edges:
                    dest_state = self.node_states.get(dest, _DetectorStates.UNVISITED)

                    # if we found a destination on the current path, error!
                    if dest_state is _DetectorStates.ON_CURRENT_PATH:
                        raise ScopeCycleError(f"A cycle was found involving '{dest}'")
                    elif dest_state is _DetectorStates.UNVISITED:
                        self.node_states[dest] = _DetectorStates.ON_CURRENT_PATH
                        self._stack_push(dest)
                        break
                    else:  # _DetectorStates.PROVEN_NO_CYCLE
                        pass  # Do nothing; don't descend.

                # 'else' means there was no break from the loop, so we explored all of
                # the out-edges of the current node and didn't find any cycles.
                # Mark off the current node, pop the stack, and let the next round of
                # iteration resume exploration of the graph.
                else:
                    self.node_states[current_node] = _DetectorStates.PROVEN_NO_CYCLE
                    self.visit_stack.pop()
