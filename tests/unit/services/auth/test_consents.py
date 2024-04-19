from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import randint
from types import SimpleNamespace
from uuid import UUID

import pytest

from globus_sdk._types import UUIDLike
from globus_sdk.experimental.consents import (
    Consent,
    ConsentForest,
    ConsentTreeConstructionError,
)

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
ScopeRepr = namedtuple("Scope", ["id", "name"])
Scopes = SimpleNamespace(
    A=ScopeRepr(_uuid_of("A"), "A"),
    B=ScopeRepr(_uuid_of("B"), "B"),
    C=ScopeRepr(_uuid_of("C"), "C"),
    D=ScopeRepr(_uuid_of("D"), "D"),
)


@dataclass
class ConsentTest(Consent):
    """
    A convenience Consent data subclass with default values for most fields to make
      test case definition less verbose.

    Required fields: client, scope, scope_name
    """

    client: UUIDLike
    scope: UUIDLike
    scope_name: str
    id: int = field(default_factory=lambda: randint(1, 10000))
    effective_identity: UUIDLike = _uuid_of("9")
    dependency_path: list[int] = field(default_factory=list)
    created: datetime = field(
        default_factory=lambda: datetime.now() - timedelta(days=1)
    )
    updated: datetime = field(
        default_factory=lambda: datetime.now() - timedelta(days=1)
    )
    last_used: datetime = field(default_factory=datetime.now)
    status: str = "approved"
    allows_refresh: bool = True
    auto_approved: bool = False
    atomically_revocable: bool = False

    def __post_init__(self):
        # Append self to the dependency path if it's not already there
        if not self.dependency_path or self.dependency_path[-1] != self.id:
            self.dependency_path.append(self.id)

    @classmethod
    def of(
        cls,
        client: str,
        scope: ScopeRepr,
        *,
        parent: ConsentTest | None = None,
        **kwargs,
    ) -> ConsentTest:
        return cls(
            client=client,
            scope=scope.id,
            scope_name=scope.name,
            dependency_path=list(parent.dependency_path) if parent else [],
            **kwargs,
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
