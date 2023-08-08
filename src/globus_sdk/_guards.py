from __future__ import annotations

import sys
import typing as t

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

T = t.TypeVar("T")


def is_list_of(data: t.Any, typ: type[T]) -> TypeGuard[list[T]]:
    return isinstance(data, list) and all(isinstance(item, typ) for item in data)


def is_optional(data: t.Any, typ: type[T]) -> TypeGuard[T | None]:
    return data is None or isinstance(data, typ)


def is_optional_list_of(data: t.Any, typ: type[T]) -> TypeGuard[list[T] | None]:
    return data is None or (
        isinstance(data, list) and all(isinstance(item, typ) for item in data)
    )
