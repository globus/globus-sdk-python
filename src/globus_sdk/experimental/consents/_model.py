"""
This module provides convenience data structures to model and interact with
    Globus Auth consents.

The resources defined herein are:
    * ``Consent``
        * A data object modeling a user's grant for a client to perform some scoped
            operation on their behalf.
        * This grant is conditional on the invocation path leading to the client's
            attempted operation being initiated through a chain of similarly scoped
            operations (consents) defined in the "dependency_path".
    * ``ConsentTree``
        * A tree composed of Consent nodes with edges modeling the dependency
            relationships between them.
        * A `meets_scope_requirements` method is defined to check whether a scope
            requirement, including dependent scope requirements, is satisfied by the
            tree.
    * ``ConsentForest``
        * A collection of all ConsentTrees for a user rooted under a particular client
            (the client that initiated the request for consents).
        * A `meets_scope_requirements` method is defined to check whether a scope
            requirement, including dependent scope requirements, is satisfied by any
            tree in the forest.
"""

from __future__ import annotations

import typing as t
from dataclasses import dataclass
from datetime import datetime

from globus_sdk import Scope
from globus_sdk._types import UUIDLike

from ._errors import ConsentParseError, ConsentTreeConstructionError


@dataclass
class Consent:
    """
    Consent Data Object

    This object models:
        * A grant which a user has provided for a client to perform a particular
            scoped operation on their behalf.
        * The consent is conditional on the invocation path leading to the client's
            attempted operation being initiated through a chain of similarly scoped
            operations (consents) defined in the "dependency_path".
    """

    client: UUIDLike
    scope: UUIDLike
    scope_name: str
    id: int
    effective_identity: UUIDLike
    # A list representing the path of consent dependencies leading from a "root consent"
    #   to this. The last element of this list will always be this consent's ID.
    # Downstream dependency relationships may exist but will not be defined here.
    dependency_path: list[int]
    created: datetime
    updated: datetime
    last_used: datetime
    status: str
    allows_refresh: bool
    auto_approved: bool
    atomically_revocable: bool

    @classmethod
    def load(cls, data: t.Mapping[str, t.Any]) -> Consent:
        """
        Load a Consent object from a raw data dictionary.

        :param data: A dictionary containing the raw consent data.
        :raises: ConsentParseError if the data is missing a required key.
        """
        try:
            return cls(
                id=data["id"],
                client=data["client"],
                scope=data["scope"],
                effective_identity=data["effective_identity"],
                dependency_path=data["dependency_path"],
                scope_name=data["scope_name"],
                created=datetime.fromisoformat(data["created"]),
                updated=datetime.fromisoformat(data["updated"]),
                last_used=datetime.fromisoformat(data["last_used"]),
                status=data["status"],
                allows_refresh=data["allows_refresh"],
                auto_approved=data["auto_approved"],
                atomically_revocable=data["atomically_revocable"],
            )
        except KeyError as e:
            raise ConsentParseError(
                f"Failed to load Consent object. Missing required key: {e}.",
                raw_consent=dict(data),
            ) from e

    def __str__(self) -> str:
        client_id = str(self.client)
        return f"Consent [{self.id}]: Client [{client_id}] -> Scope [{self.scope_name}]"


class ConsentForest:
    """
    A ConsentForest is a data structure which models relationships between Consents,
        objects describing explicit access users have granted to particular clients.
    It exists to expose a simple interface for evaluating whether resource server grant
        requirements, as defined by a scope object are satisfied.

    Consents should be retrieved from the AuthClient's `get_consents` method.

    Example usage:

    >>> auth_client = AuthClient(...)
    >>> identity_id = ...
    >>> forest = auth_client.get_consents(identity_id).to_forest()
    >>>
    >>> # Check whether the forest contains a scope relationship
    >>> dependent_scope = GCSCollectionScopeBuilder(collection_id).data_access
    >>> scope = f"{TransferScopes.all}[{dependent_scope}]"
    >>> forest.contains_scopes(scope)


    The following diagram demonstrates a Consent Forest in which a user has consented
        to a client ("CLI") initiating transfers against two collections, both of which
        require a "data_access" dynamic scope.
    Contained Scope String:
        `transfer:all[<collection1>:data_access <collection2>:data_access]`

    .. code-block:: rst

        [Consent A          ]    [Consent B                       ]
        [Client: CLI        ] -> [Client: Transfer                ]
        [Scope: transfer:all]    [Scope: <collection1>:data_access]
                |
                |                [Consent C                       ]
                |--------------> [Client: Transfer                ]
                                 [Scope: <collection2>:data_access]
    """

    def __init__(self, consents: t.Iterable[t.Mapping[str, t.Any] | Consent]):
        """
        :param consents: An iterable of consent data objects. Typically, this will be
            a ConsentForestResponse retrieved via `auth_client.get_consents(identity)`.
            This iterable may contain either raw consent data as a dict or pre-loaded
            Consents.
        """
        self.nodes = [
            consent if isinstance(consent, Consent) else Consent.load(consent)
            for consent in consents
        ]
        # Build an index on consent id for constant time lookups
        self._node_by_id = {node.id: node for node in self.nodes}

        self.edges = self._compute_edges()
        self.trees = self._build_trees()

    def _compute_edges(self) -> dict[int, set[int]]:
        """
        Compute the edges of the forest mapping parent -> child.

        A consent's parent node id is defined as the penultimate element of the
            consent's dependency path.
        A consent with dependency list of length 1 is a root node (has no parent).
        """
        edges: dict[int, set[int]] = {node.id: set() for node in self.nodes}
        for node in self.nodes:
            if len(node.dependency_path) > 1:
                parent_id = node.dependency_path[-2]
                try:
                    edges[parent_id].add(node.id)
                except KeyError as e:
                    raise ConsentTreeConstructionError(
                        f"Failed to compute forest edges. Missing parent node: {e}.",
                        consents=self.nodes,
                    ) from e
        return edges

    def _build_trees(self) -> list[ConsentTree]:
        """
        Build out the list of trees in the forest.

        A distinct tree is built out for each "root nodes" (nodes with no parents).
        """

        # A node with dependency path length 1 has no parents, so it is a root.
        roots = [node for node in self.nodes if len(node.dependency_path) == 1]
        return [ConsentTree(root.id, self) for root in roots]

    def get_node(self, consent_id: int) -> Consent:
        return self._node_by_id[consent_id]

    def meets_scope_requirements(self, scopes: Scope | str | list[Scope | str]) -> bool:
        """
        Check whether this consent meets one or more scope requirements.

        A consent forest meets a particular scope requirement if any consent tree
            inside the forest meets the scope requirements.

        :param scopes: A single scope, a list of scopes, or a scope string to check
           against the forest.
        :returns: True if all scope requirements are met, False otherwise.
        """
        for scope in _normalize_scope_types(scopes):
            if not any(tree.meets_scope_requirements(scope) for tree in self.trees):
                return False
        return True


class ConsentTree:
    """
    A tree of Consent nodes with edges modeling the dependency relationships between
        them.

    :raises: ConsentParseError if the tree cannot be constructed due to missing
       consent dependencies.
    """

    def __init__(self, root_id: int, forest: ConsentForest):
        self.root = forest.get_node(root_id)
        self.nodes = [self.root]
        self._node_by_id = {root_id: self.root}
        self.edges: dict[int, set[int]] = {}

        self._populate_connected_nodes_and_edges(forest)

    def _populate_connected_nodes_and_edges(self, forest: ConsentForest) -> None:
        """
        Populate the nodes and edges of the tree by traversing the forest.

        Nodes/Edges are included in the tree iff they are reachable from the root.
        """
        nodes_to_evaluate = {self.root.id}
        while nodes_to_evaluate:
            consent_id = nodes_to_evaluate.pop()
            consent = forest.get_node(consent_id)
            self.edges[consent.id] = forest.edges[consent.id]

            for child_id in self.edges[consent.id]:
                if child_id not in self._node_by_id:
                    self.nodes.append(forest.get_node(child_id))
                    self._node_by_id[child_id] = forest.get_node(child_id)
                    nodes_to_evaluate.add(child_id)

    def get_node(self, consent_id: int) -> Consent:
        return self._node_by_id[consent_id]

    def meets_scope_requirements(self, scope: Scope) -> bool:
        """
        Check whether this consent tree meets a particular scope requirement.

        :param scope: A Scope requirement to check against the tree.
        """
        return self._meets_scope_requirements_recursive(self.root, scope)

    def _meets_scope_requirements_recursive(self, node: Consent, scope: Scope) -> bool:
        """
        Check recursively whether a consent node meets the scope requirements defined
            by a scope object.
        """
        if node.scope_name != scope.scope_string:
            return False

        for dependent_scope in scope.dependencies:
            for child_id in self.edges[node.id]:
                if self._meets_scope_requirements_recursive(
                    self.get_node(child_id), dependent_scope
                ):
                    # We found a child containing this full dependent scope tree
                    # Move onto the next dependent scope tree
                    break
            else:
                # We didn't find any child containing this full dependent scope tree
                return False
        # We found at least one child containing each full dependent scope tree
        return True

    @property
    def max_depth(self) -> int:
        return self._max_depth_recursive(self.root, 1)

    def _max_depth_recursive(self, node: Consent, depth: int) -> int:
        if len(self.edges[node.id]) == 0:
            return depth
        return max(
            self._max_depth_recursive(self.get_node(child_id), depth + 1)
            for child_id in self.edges[node.id]
        )

    def __str__(self) -> str:
        """Returns a textual representation of the tree to stdout (one line per node)"""
        return self._str_recursive(self.root, 0)

    def _str_recursive(self, node: Consent, tab_depth: int) -> str:
        _str = f"{' ' * tab_depth} - {node}"
        for child_id in self.edges[node.id]:
            _str += "\n" + self._str_recursive(self.get_node(child_id), tab_depth + 2)
        return _str


def _normalize_scope_types(scopes: Scope | str | list[Scope | str]) -> list[Scope]:
    """
    Normalize the input scope types into a list of Scope objects.

    Strings are parsed into 1 or more Scopes using `Scope.parse`.

    :param scopes: Some collection of 0 or more scopes as Scope or scope strings.
    :returns: A list of Scope objects.
    """

    if isinstance(scopes, Scope):
        return [scopes]
    elif isinstance(scopes, str):
        return Scope.parse(scopes)
    else:
        scope_list = []
        for scope in scopes:
            if isinstance(scope, str):
                scope_list.extend(Scope.parse(scope))
            else:
                scope_list.append(scope)
        return scope_list
