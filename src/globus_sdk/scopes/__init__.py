from ._normalize import scopes_to_scope_list, scopes_to_str
from .builder import ScopeBuilder
from .data import (
    AuthScopes,
    FlowsScopes,
    GCSCollectionScopeBuilder,
    GCSEndpointScopeBuilder,
    GroupsScopes,
    NexusScopes,
    SearchScopes,
    TimerScopes,
    TransferScopes,
)
from .errors import ScopeCycleError, ScopeParseError
from .representation import Scope
from .scope_definition import MutableScope

__all__ = (
    "ScopeBuilder",
    "MutableScope",
    "Scope",
    "ScopeParseError",
    "ScopeCycleError",
    "GCSCollectionScopeBuilder",
    "GCSEndpointScopeBuilder",
    "AuthScopes",
    "FlowsScopes",
    "GroupsScopes",
    "NexusScopes",
    "SearchScopes",
    "TimerScopes",
    "TransferScopes",
    "scopes_to_str",
    "scopes_to_scope_list",
)
