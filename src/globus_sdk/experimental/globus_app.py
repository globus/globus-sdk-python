from __future__ import annotations

import sys
import typing as t

__all__ = (
    "GlobusApp",
    "UserApp",
    "ClientApp",
    "GlobusAppConfig",
    "TokenValidationErrorHandler",
)

# legacy aliases
# (when accessed, these will emit deprecation warnings)
if t.TYPE_CHECKING:
    from globus_sdk.globus_app import (
        ClientApp,
        GlobusApp,
        GlobusAppConfig,
        TokenValidationErrorHandler,
        UserApp,
    )
else:

    def __getattr__(name: str) -> t.Any:
        import globus_sdk.globus_app as globus_app_module
        from globus_sdk.exc import warn_deprecated

        # Certain GlobusApp constructs are exposed from `globus_sdk`.
        new_import_path = f"globus_sdk.globus_app.{name}"
        if name in ("GlobusApp", "UserApp", "ClientApp", "GlobusAppConfig"):
            new_import_path = f"globus_sdk.{name}"

        warn_deprecated(
            "'globus_sdk.experimental.globus_app' has been renamed to "
            "'globus_sdk.globus_app'. "
            f"Importing '{name}' from `globus_sdk.experimental` is deprecated. "
            f"Use `{new_import_path}` instead."
        )

        value = getattr(globus_app_module, name, None)
        if value is None:
            raise AttributeError(f"module {__name__} has no attribute {name}")
        setattr(sys.modules[__name__], name, value)
        return value
