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
    from globus_sdk.gare import GlobusAuthorizationParameters
    from globus_sdk.gare import has_gares as has_auth_requirements_errors
    from globus_sdk.gare import is_gare as is_auth_requirements_error
    from globus_sdk.gare import to_gare as to_auth_requirements_error
    from globus_sdk.gare import to_gares as to_auth_requirements_errors
else:

    _RENAMES = {
        "GlobusAuthRequirementsError": "GARE",
        "to_auth_requirements_error": "to_gare",
        "to_auth_requirements_errors": "to_gares",
        "is_auth_requirements_error": "is_gare",
        "has_auth_requirements_errors": "has_gares",
    }

    def __getattr__(name: str) -> t.Any:
        import globus_sdk.gare as gare_module
        from globus_sdk.exc import warn_deprecated

        new_name = _RENAMES.get(name, name)

        warn_deprecated(
            "'globus_sdk.experimental.auth_requirements_error' has been renamed to "
            "'globus_sdk.gare'. "
            f"Importing '{name}' from `globus_sdk.experimental` is deprecated. "
            f"Use `globus_sdk.gare.{new_name}` instead."
        )

        value = getattr(gare_module, new_name, None)
        if value is None:
            raise AttributeError(f"module {__name__} has no attribute {name}")
        setattr(sys.modules[__name__], name, value)
        return value
