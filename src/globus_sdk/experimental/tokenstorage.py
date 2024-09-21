from __future__ import annotations

import sys
import typing as t

__all__ = (
    "JSONTokenStorage",
    "SQLiteTokenStorage",
    "TokenStorage",
    "FileTokenStorage",
    "MemoryTokenStorage",
    "TokenStorageData",
)

# legacy aliases
# (when accessed, these will emit deprecation warnings)
if t.TYPE_CHECKING:
    from globus_sdk.tokenstorage import (
        FileTokenStorage,
        JSONTokenStorage,
        MemoryTokenStorage,
        SQLiteTokenStorage,
        TokenStorage,
        TokenStorageData,
    )
else:

    def __getattr__(name: str) -> t.Any:
        import globus_sdk.tokenstorage as tokenstorage_module
        from globus_sdk.exc import warn_deprecated

        warn_deprecated(
            "'globus_sdk.experimental.tokenstorage' has been renamed to "
            "'globus_sdk.tokenstorage'. "
            f"Importing '{name}' from `globus_sdk.experimental` is deprecated. "
            f"Use `globus_sdk.tokenstorage.{name}` instead."
        )

        value = getattr(tokenstorage_module, name, None)
        if value is None:
            raise AttributeError(f"module {__name__} has no attribute {name}")
        setattr(sys.modules[__name__], name, value)
        return value
