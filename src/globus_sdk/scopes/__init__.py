from ._normalize import scopes_to_scope_list, scopes_to_str
from .builder import ScopeBuilder
from .data import (
    AuthScopes,
    ComputeScopes,
    FlowsScopes,
    GCSCollectionScopeBuilder,
    GCSEndpointScopeBuilder,
    GroupsScopes,
    NexusScopes,
    SearchScopes,
    SpecificFlowScopeBuilder,
    TimersScopes,
    TransferScopes,
)
from .errors import ScopeCycleError, ScopeParseError
from .representation import Scope

__all__ = (
    "ScopeBuilder",
    "Scope",
    "ScopeParseError",
    "ScopeCycleError",
    "GCSCollectionScopeBuilder",
    "GCSEndpointScopeBuilder",
    "AuthScopes",
    "ComputeScopes",
    "FlowsScopes",
    "SpecificFlowScopeBuilder",
    "GroupsScopes",
    "NexusScopes",
    "SearchScopes",
    "TimersScopes",
    "TransferScopes",
    "scopes_to_str",
    "scopes_to_scope_list",
)
