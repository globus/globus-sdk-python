from __future__ import annotations

import os
import typing as t
import warnings


# this is (by meaning) a type of DeprecationWarning, but because python suppresses
# DeprecationWarning by default, most users would never see it if we inherited from that
# therefore, inheriting from Warning is an "incorrect" but pragmatic choice
#
# in concert with the helpers below to make the warnings opt-in, this results in good
# user-facing behavior
class GlobusSDKLegacyBehaviorWarning(Warning):
    def __init__(
        self,
        message: str,
        *args: t.Any,
        will_be_removed: str | None = "4.0.0",
        **kwargs: t.Any,
    ) -> None:
        super().__init__(message, *args, **kwargs)
        self.message = message
        self.will_be_removed = will_be_removed

    def __str__(self) -> str:
        if self.will_be_removed is None:
            return self.message
        else:
            return (
                f"{self.message} (support for this will be removed in "
                f"globus-sdk version {self.will_be_removed})"
            )


def warn_deprecated(message: str, stacklevel: int = 2) -> None:
    if not _deprecation_warnings_enabled():
        return

    warnings.warn(message, GlobusSDKLegacyBehaviorWarning, stacklevel=stacklevel)


def _deprecation_warnings_enabled() -> bool:
    var = os.getenv("GLOBUS_SDK_V4_WARNINGS", "false").lower()
    if var in ("true", "yes", "on", "1"):
        return True
    return False
