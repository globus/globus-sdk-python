"""
Scope parsing has been moved out of experimental into the main SDK.
This module will be removed in a future release but is maintained in the interim for
  backwards compatibility.
"""

from globus_sdk.scopes import Scope, ScopeCycleError, ScopeParseError

__all__ = (
    "Scope",
    "ScopeParseError",
    "ScopeCycleError",
)
