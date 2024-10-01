import sys
import typing as t

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
    "ComputeScopes",
    "FlowsScopes",
    "SpecificFlowScopeBuilder",
    "GroupsScopes",
    "NexusScopes",
    "SearchScopes",
    "TimerScopes",
    "TimersScopes",
    "TransferScopes",
    "scopes_to_str",
    "scopes_to_scope_list",
)


if t.TYPE_CHECKING:
    TimerScopes = TimersScopes
else:

    def __getattr__(name: str) -> t.Any:
        from globus_sdk.exc import warn_deprecated

        if name == "TimerScopes":
            warn_deprecated(
                "'TimerScopes' is a deprecated name. Use 'TimersScopes' instead."
            )
            setattr(sys.modules[__name__], name, TimersScopes)
            return TimersScopes
        raise AttributeError(f"module {__name__} has no attribute {name}")
