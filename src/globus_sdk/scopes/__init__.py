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
from .scope_definition import Scope, ScopeParseError

# alias to old name
#
# deprecation TODO:
# - add a `__getattr__` on this module which raises a deprecation warning on access to
#   `MutableScope`
# - ensure removal in SDK v4.0
#   (add a test case which checks the version and fails if this is present and the
#    version is >=4 ?)
MutableScope = Scope


__all__ = (
    "ScopeBuilder",
    "Scope",
    "ScopeParseError",
    "GCSCollectionScopeBuilder",
    "GCSEndpointScopeBuilder",
    "AuthScopes",
    "FlowsScopes",
    "GroupsScopes",
    "NexusScopes",
    "SearchScopes",
    "TimerScopes",
    "TransferScopes",
)
