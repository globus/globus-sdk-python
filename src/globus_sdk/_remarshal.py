"""
This module provides internal helpers for remarshalling data from one shape
into another.

This may be as simple as converting strings from one form to another, or as
sophisticated as building a specific internal object in a configurable way.
"""

from __future__ import annotations

import collections.abc
import typing as t
import uuid

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._types import UUIDLike

T = t.TypeVar("T")
R = t.TypeVar("R")


def safe_strseq_iter(
    value: t.Iterable[t.Any] | str | uuid.UUID,
) -> t.Iterator[str]:
    """
    Iterate over one or more string/string-convertible values.

    :param value: The stringifiable object or objects to iterate over

    This is a passthrough with some caveats:
    - if the value is a solitary string, yield only that value
    - if the value is a solitary UUID, yield only that value (as a string)
    - str values in the iterable which are not strings

    This helps handle cases where a string is passed to a function expecting an iterable
    of strings, as well as cases where an iterable of UUID objects is accepted for a
    list of IDs, or something similar.
    """
    if isinstance(value, str):
        yield value
    elif isinstance(value, uuid.UUID):
        yield str(value)
    else:
        for x in value:
            yield str(x)


def safe_stringify(value: object | MissingType | None) -> str | MissingType | None:
    """
    Convert a value to a string, with handling for None and Missing.

    :param value: The stringifiable object
    """
    if value is None:
        return None
    if isinstance(value, MissingType):
        return MISSING
    return str(value)


@t.overload
def safe_strseq_listify(value: None) -> None: ...
@t.overload
def safe_strseq_listify(value: MissingType) -> MissingType: ...
@t.overload
def safe_strseq_listify(value: t.Iterable[t.Any] | str | uuid.UUID) -> list[str]: ...


def safe_strseq_listify(
    value: t.Iterable[t.Any] | str | uuid.UUID | MissingType | None,
) -> list[str] | MissingType | None:
    """
    A wrapper over safe_strseq_iter which produces list outputs.
    This method takes responsibility for checking for MISSING and None values.

    Unlike safe_strseq_iter, this may be the "last mile" remarshalling step before
    data is actually passed to the network layer. Therefore, it makes sense for this
    helper to handle (MISSING | None).

    :param value: The stringifiable object or iterable of objects
    """
    if value is None:
        return None
    if isinstance(value, MissingType):
        return MISSING
    return list(safe_strseq_iter(value))


@t.overload
def listify(value: None) -> None: ...
@t.overload
def listify(value: MissingType) -> MissingType: ...
@t.overload
def listify(value: t.Iterable[T]) -> list[T]: ...


def listify(value: t.Iterable[T] | MissingType | None) -> list[T] | MissingType | None:
    """
    Convert any iterable to a list, with handling for None and Missing.

    :param value: The iterable of objects
    """
    if value is None:
        return None
    if isinstance(value, MissingType):
        return MISSING
    if isinstance(value, list):
        return value
    return list(value)


@t.overload
def safe_list_map(value: None, mapped_function: t.Callable[[T], R]) -> None: ...


@t.overload
def safe_list_map(
    value: MissingType, mapped_function: t.Callable[[T], R]
) -> MissingType: ...


@t.overload
def safe_list_map(
    value: t.Iterable[T], mapped_function: t.Callable[[T], R]
) -> list[R]: ...


def safe_list_map(
    value: t.Iterable[T] | MissingType | None, mapped_function: t.Callable[[T], R]
) -> list[R] | MissingType | None:
    """
    Like map() but handles None|MISSING and listifies the result otherwise.

    :param value: The iterable of objects over which to map
    :param mapped_function: The function to map
    """
    if value is None:
        return None
    if isinstance(value, MissingType):
        return MISSING
    return [mapped_function(element) for element in value]


@t.overload
def commajoin(value: MissingType) -> MissingType: ...
@t.overload
def commajoin(value: UUIDLike | t.Iterable[UUIDLike]) -> str: ...


def commajoin(
    value: UUIDLike | t.Iterable[UUIDLike] | MissingType,
) -> str | MissingType:
    # note that this explicit handling of Iterable allows for string-like objects to be
    # passed to this function and be stringified by the `str()` call
    if isinstance(value, MissingType):
        return value
    if isinstance(value, collections.abc.Iterable):
        return ",".join(safe_strseq_iter(value))
    return str(value)
