from __future__ import annotations

import json
import typing as t
from dataclasses import dataclass
from datetime import datetime

from globus_sdk import Scope
from globus_sdk._types import UUIDLike

from .errors import ConsentParseError


@dataclass
class Consent:
    """
    Consent Data Object

    This object represents:
        1. A grant that a user has given to a client to access a scope on their behalf.
        2. The path of upstream dependent consents leading from a "root consent" to this
           one.
    """

    id: int
    client: UUIDLike
    scope: UUIDLike
    effective_identity: UUIDLike
    # A list representing the path of consent dependencies lading from a "root consent"
    #   to this. The last element of this list will always be this consent's ID.
    # Downstream dependency relationships may exist but are not defined here.
    dependency_path: list[int]
    scope_name: str
    created: datetime
    updated: datetime
    last_used: datetime
    status: str
    allows_refresh: bool
    auto_approved: bool
    atomically_revocable: bool

    @classmethod
    def load(cls, data: t.Mapping[str, t.Any]) -> Consent:
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
                f"Failed to load Consent object. Missing required key: {e}. "
                f"Raw Consent: {json.dumps(data)}."
            )


class ConsentForest:
    """
    A Consent Forest is a data structure which models Consent objects, retrieved from
        the `auth.get_consents` API endpoint, and their relationships to each other.

    The main purpose of the forest is to expose a simple interface for asking
        whether one or more scope trees (a root scope plus dynamic dependent scopes)
        are contained in a user's consents.

    A `Consent`, on its own, describes a "grant" that a user has given to a particular
        client to access a particular scope on their behalf.
    A `ConsentForest` is a directed acyclic graph with nodes representing `Consents`
        and edges representing the dependency relationship between them.
    With these two facts in mind, the ConsentForest broadly represents the chain of
        grants that a user has given to various clients consenting that they may
        access various scopes on their behalf.

    The following diagram demonstrates a Consent Forest in which a user has consented
        to a client ("CLI") initiating transfers against two collections, both of which
        require a "data_access" dynamic scope.
    Contained Scope String:
        `transfer:all[<collection1>:data_access <collection2>:data_access]`
    ```
    [Consent A          ]    [Consent B                       ]
    [Client: CLI        ] -> [Client: Transfer                ]
    [Scope: transfer:all]    [Scope: <collection1>:data_access]
            |
            |                [Consent C                       ]
            |--------------> [Client: Transfer                ]
                             [Scope: <collection2>:data_access]
    ```
    """

    def __init__(self, consents: t.Iterable[t.Mapping[str, t.Any]]):
        # Raw consent nodes, indexed by their ID
        self._consents: dict[int, Consent] = {}
        for consent_data in consents:
            consent = Consent.load(consent_data)
            self._consents[consent.id] = consent

        # Consent edge mappings.
        self._direct_children = {cid: set() for cid in self._consents.keys()}
        for consent in self._consents.values():
            if len(consent.dependency_path) > 1:
                upstream_id = consent.dependency_path[-2]
                self._direct_children[upstream_id].add(consent.id)

        # The collection of root consents in the forest where traversal should begin.
        # These consents are indexed by their scope name rather than consent id in order
        #   to simplify the scope tree evaluation operation.
        roots = [c for c in self._consents.values() if len(c.dependency_path) == 1]
        self._root_consents_by_scope = {root.scope_name: root for root in roots}

    @property
    def nodes(self) -> dict[int, Consent]:
        return self._consents

    def get_node(self, consent_id: int) -> Consent:
        return self._consents[consent_id]

    @property
    def edges(self) -> dict[int, set[int]]:
        return self._direct_children

    def contains_scopes(self, scopes: Scope | str | list[Scope | str]) -> bool:
        """
        Check whether this consent forest contains one or more scope trees.

        A consent forest "contains a scope tree" if
            * There exists a root consent whose scope matches the root scope string.
            * At least one child consent (from that root) contains each dependent scope.
        """
        for scope in _normalize_scope_types(scopes):
            if (root := self._root_consents_by_scope.get(scope.scope_string)) is None:
                return False

            if not self._contains_scope(root, scope):
                return False
        return True

    def _contains_scope(self, node: Consent, scope: Scope) -> bool:
        """
        Check recursively whether a consent node contains the full scope
          tree defined by a scope object.
        """

        if node.scope_name != scope.scope_string:
            return False

        for dependent_scope in scope.dependencies:
            for child_id in self._direct_children[node.id]:
                if self._contains_scope(self._consents[child_id], dependent_scope):
                    # We found a child containing this full dependent scope tree
                    # Move onto the next dependent scope tree
                    break
            else:
                # We didn't find any child containing this full dependent scope tree
                return False
        # We found at least one child containing each full dependent scope tree
        return True

    def print_tree(self, consent_id: int, tab_depth: int = 0):
        """
        Print a visual representation of consent tree rooted at consent_id.

        Example Output:
        >>> consent_forest.print_tree(1234567)
        >>> # - [1234567] transfer:all
        >>> #  - [1234568] groups:view_my_groups
        >>> #  - [1234569] <collection>:data_access
        """
        consent = self._consents[consent_id]
        print(f"{' ' * tab_depth} - [{consent_id}] {consent.scope_name}")
        for child_id in self._direct_children[consent_id]:
            self.print_tree(child_id, tab_depth + 2)


def _normalize_scope_types(scopes: Scope | str | list[Scope | str]) -> list[Scope]:
    """
    Normalize the input scope types into a list of Scope objects.

    Strings are parsed into 1 or more Scopes using `Scope.parse`.
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
