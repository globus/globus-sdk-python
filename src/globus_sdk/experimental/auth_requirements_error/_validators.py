from __future__ import annotations

import sys
import typing as t

from globus_sdk import _guards

from ._serializable import Serializable

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

T = t.TypeVar("T")
S = t.TypeVar("S", bound=Serializable)


class ValidationError(ValueError):
    pass


def _from_guard(
    check: t.Callable[[t.Any], TypeGuard[T]], description: str
) -> t.Callable[[str, t.Any], T]:
    def validator(name: str, value: t.Any) -> T:
        if check(value):
            return value
        raise ValidationError(f"'{name}' must be {description}")

    return validator


str_ = _from_guard(_guards.reduce(str).apply, "a string")
opt_str = _from_guard(_guards.reduce(str).optional, "a string or null")
opt_bool = _from_guard(_guards.reduce(bool).optional, "a bool or null")
str_list = _from_guard(_guards.reduce(str).list_of, "a list of strings")
opt_str_list = _from_guard(
    _guards.reduce(str).optional_list, "a list of strings or null"
)


def opt_str_list_or_commasep(name: str, value: t.Any) -> list[str] | None:
    if _guards.is_optional_list_of(value, str):
        return value
    if isinstance(value, str):
        return value.split(",")
    raise ValidationError(
        f"'{name}' must be a list of strings or a comma-delimited string or null"
    )


def instance_or_dict(name: str, value: t.Any, cls: type[S]) -> S:
    if isinstance(value, cls):
        return value
    if isinstance(value, dict):
        return cls.from_dict(value)
    raise ValidationError(f"'{name}' must be a '{cls.__name__}' object or a dictionary")
