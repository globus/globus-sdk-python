from __future__ import annotations

import sys
import typing as t

from .timers import TimersAPIError, TimersClient

__all__ = (
    "TimerAPIError",
    "TimerClient",
)

# legacy aliases
# (when accessed, these will emit deprecation warnings in a future release)
if t.TYPE_CHECKING:
    TimerClient = TimersClient
    TimerAPIError = TimersAPIError
else:
    _RENAMES: dict[str, tuple[str, type]] = {
        "TimerClient": ("TimersClient", TimersClient),
        "TimerAPIError": ("TimersAPIError", TimersAPIError),
    }

    def __getattr__(name: str) -> t.Any:
        # In the future, add the following snippet or similar to emit
        # deprecation warnings:
        #
        # from globus_sdk.exc import warn_deprecated
        #
        # if name in _RENAMES:
        #     new_name = _RENAMES[name][0]
        #     warn_deprecated(
        #         f"'globus_sdk.{name}' has been renamed to 'globus_sdk.{new_name}'. "
        #         "'{name}' is supported as an alias for now."
        #     )
        if name in _RENAMES:
            value = _RENAMES[name][1]
            setattr(sys.modules[__name__], name, value)
            return value

        raise AttributeError(f"module {__name__} has no attribute {name}")
