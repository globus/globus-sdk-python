from __future__ import annotations

import sys
import typing as t

__all__ = (
    "GlobusAuthRequirementsError",
    "GlobusAuthorizationParameters",
    "to_auth_requirements_error",
    "to_auth_requirements_errors",
    "is_auth_requirements_error",
    "has_auth_requirements_errors",
)

# legacy aliases
# (when accessed, these will emit deprecation warnings)
if t.TYPE_CHECKING:
    from globus_sdk.gare import GARE as GlobusAuthRequirementsError
    from globus_sdk.gare import (
        GlobusAuthorizationParameters,
        has_auth_requirements_errors,
        is_auth_requirements_error,
        to_auth_requirements_error,
        to_auth_requirements_errors,
    )
else:

    def __getattr__(name: str) -> t.Any:
        import globus_sdk.gare as gare_module
        from globus_sdk.exc import warn_deprecated

        warn_deprecated(
            "'globus_sdk.experimental.auth_requirements_error' has been renamed to "
            "'globus_sdk.gare'. "
            f"Importing '{name}' from `globus_sdk.experimental` is deprecated."
        )

        # rename GlobusAuthRequirementsError -> GARE
        if name == "GlobusAuthRequirementsError":
            name = "GARE"

        value = getattr(gare_module, name, None)
        if value is None:
            raise AttributeError(f"module {__name__} has no attribute {name}")
        setattr(sys.modules[__name__], name, value)
        return value
