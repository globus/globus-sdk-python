from ._normalize import scopes_to_scope_list, scopes_to_str
from .collection import DynamicScopeCollection, ScopeCollection, StaticScopeCollection
from .data import (
    AuthScopes,
    ComputeScopes,
    FlowsScopes,
    GCSCollectionScopes,
    GCSEndpointScopes,
    GroupsScopes,
    NexusScopes,
    SearchScopes,
    SpecificFlowScopes,
    TimersScopes,
    TransferScopes,
)
from .errors import ScopeCycleError, ScopeParseError
from .parser import ScopeParser
from .representation import Scope

__all__ = (
    "ScopeCollection",
    "StaticScopeCollection",
    "DynamicScopeCollection",
    "Scope",
    "ScopeParser",
    "ScopeParseError",
    "ScopeCycleError",
    "GCSCollectionScopes",
    "GCSEndpointScopes",
    "AuthScopes",
    "ComputeScopes",
    "FlowsScopes",
    "SpecificFlowScopes",
    "GroupsScopes",
    "NexusScopes",
    "SearchScopes",
    "TimersScopes",
    "TransferScopes",
    "scopes_to_str",
    "scopes_to_scope_list",
)
