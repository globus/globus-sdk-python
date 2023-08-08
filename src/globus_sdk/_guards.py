from __future__ import annotations

import sys
import typing as t

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

T = t.TypeVar("T")


def is_list_of(data: t.Any, typ: type[T]) -> TypeGuard[list[T]]:
    if isinstance(data, list):
        return all(isinstance(item, typ) for item in data)
    return False
