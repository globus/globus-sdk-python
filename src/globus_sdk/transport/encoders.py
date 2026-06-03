from __future__ import annotations

import sys

from .representation_providers import (
    RequestsHttpFormProvider,
    RequestsJsonProvider,
    RequestsPlainTextProvider,
)

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


# shim these class names until the next major SDK version, at which point they can be
# removed
#
# ideally, after soft-deprecation, we should start emitting deprecation warnings when
# these names are imported, but this will also require handling in __init__.py

RequestEncoder: TypeAlias = RequestsPlainTextProvider
JSONRequestEncoder: TypeAlias = RequestsJsonProvider
FormRequestEncoder: TypeAlias = RequestsHttpFormProvider
