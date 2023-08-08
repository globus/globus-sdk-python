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


def reduce(typ: type[T]) -> _Reducer[T]:
    """
    reduce and the supporting _Reducer class provide a transform on existing type
    guards, defined above.

    The basic transform is from a check over two parameters to a check over one
    (input) parameter.

    e.g. The following two guards are the same:
        is_list_of(data, str)
        reduce(str).list_of(data)

    The effect is to produce a simpler call signature which is easier to chain
    or otherwise modify.
    """
    return _Reducer(typ)


class _Reducer(t.Generic[T]):
    def __init__(self, typ: type[T]):
        self.typ = typ

    # although it might be nice to use __call__ here, type checkers (read: mypy) do not
    # always correctly treat an arbitrary callable TypeGuard as a a guard
    def apply(self, data: t.Any) -> TypeGuard[T]:
        return isinstance(data, self.typ)

    def list_of(self, data: t.Any) -> TypeGuard[list[T]]:
        return is_list_of(data, self.typ)

    def optional(self, data: t.Any) -> TypeGuard[T | None]:
        return is_optional(data, self.typ)

    def optional_list(self, data: t.Any) -> TypeGuard[list[T] | None]:
        return is_optional_list_of(data, self.typ)
