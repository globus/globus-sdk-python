from __future__ import annotations

import typing as t

from .representation_providers import (
    RequestsHttpFormProvider,
    RequestsJsonProvider,
    RequestsPlainTextProvider,
)

# shim these class names until the next major SDK version, at which point they can be
# removed
#
# ideally, after soft-deprecation, we should start emitting deprecation warnings when
# these names are imported, but this will also require handling in __init__.py

RequestEncoder: t.TypeAlias = RequestsPlainTextProvider
JSONRequestEncoder: t.TypeAlias = RequestsJsonProvider
FormRequestEncoder: t.TypeAlias = RequestsHttpFormProvider
