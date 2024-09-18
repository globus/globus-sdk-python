from __future__ import annotations

import sys
import typing as t

__all__ = (
    "CommandLineLoginFlowManager",
    "LocalServerLoginFlowManager",
    "LoginFlowManager",
)

# legacy aliases
# (when accessed, these will emit deprecation warnings)
if t.TYPE_CHECKING:
    from globus_sdk.login_flows import (
        CommandLineLoginFlowManager,
        LocalServerLoginFlowManager,
        LoginFlowManager,
    )
else:

    def __getattr__(name: str) -> t.Any:
        import globus_sdk.login_flows as login_flows_module
        from globus_sdk.exc import warn_deprecated

        warn_deprecated(
            "'globus_sdk.experimental.login_flow_manager' has been renamed to "
            "'globus_sdk.login_flows'. "
            f"Importing '{name}' from `globus_sdk.experimental` is deprecated. "
            f"Use `globus_sdk.login_flows.{name}` instead."
        )

        value = getattr(login_flows_module, name, None)
        if value is None:
            raise AttributeError(f"module {__name__} has no attribute {name}")
        setattr(sys.modules[__name__], name, value)
        return value
