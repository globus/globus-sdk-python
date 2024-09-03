from __future__ import annotations

import uuid
from collections import defaultdict, namedtuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from globus_sdk import Scope
from globus_sdk._types import UUIDLike
from globus_sdk.experimental.consents import Consent, ConsentForest

ScopeRepr = namedtuple("Scope", ["id", "name"])


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
    id: int = field(default_factory=lambda: uuid.uuid1().int)
    effective_identity: UUIDLike = str(uuid.uuid4())
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


def make_consent_forest(scopes: list[str | Scope] | str | Scope) -> ConsentForest:
    """
    Creates a consent forest from a list of scope strings or scope objects.
    Client and Scope IDs are generated at random.
    """
    _scopes = _normalize_scopes(scopes)
    scope_id_mapping: dict[str, str] = defaultdict(lambda: str(uuid.uuid4()))
    consents = []
    for scope in _scopes:
        consents.extend(_generate_consents(scope, scope_id_mapping))
    return ConsentForest(consents)


def _normalize_scopes(scopes: list[str | Scope] | str | Scope) -> list[Scope]:
    if isinstance(scopes, Scope):
        return [scopes]
    elif isinstance(scopes, str):
        return Scope.parse(scopes)
    else:
        to_return = []
        for scope in scopes:
            to_return.extend(_normalize_scopes(scope))
        return to_return


def _generate_consents(
    scope: Scope, scope_id_mapping: dict[str, str], parent: ConsentTest | None = None
) -> list[Consent]:
    """Generates a list of consents for a scope and its children."""
    consents = []
    client_id = str(uuid.uuid4())
    scope_string = scope.scope_string
    scope_id = scope_id_mapping[scope_string]
    consent = ConsentTest.of(
        client_id, ScopeRepr(scope_id, scope_string), parent=parent
    )
    consents.append(consent)
    for dependent_scope in scope.dependencies:
        consents.extend(
            _generate_consents(dependent_scope, scope_id_mapping, parent=consent)
        )
    return consents
