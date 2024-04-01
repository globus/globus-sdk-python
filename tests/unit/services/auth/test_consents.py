from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

import pytest

from globus_sdk.experimental.consents import ConsentForest, ConsentTreeConstructionError
from tests.common import ConsentTest, ScopeRepr

_zero_uuid = str(UUID(int=0))


def _uuid_of(char: str) -> str:
    if len(char) != 1:
        raise ValueError(f"char must be a single character, got {char!r}")
    return _zero_uuid.replace("0", char)


Clients = SimpleNamespace(
    Zero=_uuid_of("0"),
    One=_uuid_of("1"),
    Two=_uuid_of("2"),
    Three=_uuid_of("3"),
)
Scopes = SimpleNamespace(
    A=ScopeRepr(_uuid_of("A"), "A"),
    B=ScopeRepr(_uuid_of("B"), "B"),
    C=ScopeRepr(_uuid_of("C"), "C"),
    D=ScopeRepr(_uuid_of("D"), "D"),
)


def test_consent_forest_creation():
    root = ConsentTest.of(Clients.Zero, Scopes.A)
    node1 = ConsentTest.of(Clients.One, Scopes.B, parent=root)
    node2 = ConsentTest.of(Clients.Two, Scopes.C, parent=node1)

    forest = ConsentForest([root, node1, node2])
    assert len(forest.trees) == 1
    tree = forest.trees[0]
    assert tree.root == root
    assert tree.max_depth == 3

    assert tree.edges[tree.root.id] == {node1.id}
    assert tree.edges[node1.id] == {node2.id}
    assert tree.edges[node2.id] == set()

    assert tree.get_node(root.id) == root
    assert tree.get_node(node1.id) == node1
    assert tree.get_node(node2.id) == node2


def test_consent_forest_scope_requirement_evaluation():
    root = ConsentTest.of(Clients.Zero, Scopes.A)
    node1 = ConsentTest.of(Clients.One, Scopes.B, parent=root)
    node2 = ConsentTest.of(Clients.Two, Scopes.C, parent=node1)

    forest = ConsentForest([root, node1, node2])

    assert forest.meets_scope_requirements("A")
    assert forest.meets_scope_requirements("A[B[C]]")
    assert not forest.meets_scope_requirements("B")
    assert not forest.meets_scope_requirements("A[C]")


def test_consent_forest_scope_requirement_with_sibling_dependent_scopes():
    root = ConsentTest.of(Clients.Zero, Scopes.A)
    node1 = ConsentTest.of(Clients.One, Scopes.B, parent=root)
    node2 = ConsentTest.of(Clients.Two, Scopes.C, parent=root)

    forest = ConsentForest([root, node1, node2])

    assert forest.meets_scope_requirements("A")
    assert forest.meets_scope_requirements("A[B]")
    assert forest.meets_scope_requirements("A[C]")
    assert forest.meets_scope_requirements("A[B C]")
    assert not forest.meets_scope_requirements("A[B[C]]")
    assert not forest.meets_scope_requirements("A[C[B]]")


@pytest.mark.parametrize("atomically_revocable", (True, False))
def test_consent_forest_scope_requirement_with_optional_dependent_scopes(
    atomically_revocable: bool,
):
    """
    Dependent scope optionality is intentionally ignored for this implementation.

    In formal terms, the scope "A[*B]" is only satisfied by a tree matching the shape
      A -> B where B is "atomically revocable".
    We've decided that this is an auth service concern, not a concern for local clients
      to be making decisions about; so we intentionally ignore this distinction in order
      to give standard users a simpler verification mechanism to ask "will my request
      work with the current set of consents?".
    """
    root = ConsentTest.of(Clients.Zero, Scopes.A)
    child = ConsentTest.of(
        Clients.One, Scopes.B, parent=root, atomically_revocable=atomically_revocable
    )

    forest = ConsentForest([root, child])

    assert forest.meets_scope_requirements("A[B]")
    assert forest.meets_scope_requirements("A[*B]")


def test_consent_forest_with_disjoint_consents_with_duplicate_scopes():
    """
    Strange state to reproduce in practice but this test case simulates the forest of
      Tree 1: A (Client Zero) -> B (Client Zero)
      Tree 2: B (Client Zero) -> C (Client Zero)

    In this situation, A[B] and B[C] are both satisfied, but A[B[C]] is not.
    """
    root1 = ConsentTest.of(Clients.Zero, Scopes.A)
    child1 = ConsentTest.of(Clients.Zero, Scopes.B, parent=root1)

    root2 = ConsentTest.of(Clients.Zero, Scopes.B)
    child2 = ConsentTest.of(Clients.Zero, Scopes.C, parent=root2)

    forest = ConsentForest([root1, child1, root2, child2])

    assert forest.meets_scope_requirements("A[B]")
    assert forest.meets_scope_requirements("B[C]")
    assert not forest.meets_scope_requirements("A[B[C]]")


def test_consent_forest_with_missing_intermediary_nodes():
    """
    Simulate a situation in which we didn't receive the full list of consents from
      Auth. So the tree has holes

    Tree: A -> <B should be here but isn't> -> C
    """
    root = ConsentTest.of(Clients.Zero, Scopes.A)
    node1 = ConsentTest.of(Clients.One, Scopes.B, parent=root)
    node2 = ConsentTest.of(Clients.Two, Scopes.C, parent=node1)

    # Only add the first and last node to the forest.
    # The last node (C) references the middle node (B) and so forest loading should
    #   fail.
    with pytest.raises(
        ConsentTreeConstructionError, match=rf"Missing parent node: {node1.id}"
    ):
        ConsentForest([root, node2])
