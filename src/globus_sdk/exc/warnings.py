from __future__ import annotations

import warnings


class RemovedInV4Warning(DeprecationWarning):
    pass


def warn_deprecated(message: str, stacklevel: int = 2) -> None:
    warnings.warn(message, RemovedInV4Warning, stacklevel=stacklevel)
