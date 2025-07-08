"""
This module provides internal helpers for remarshalling data from one shape
into another.

This may be as simple as converting strings from one form to another, or as
sophisticated as building a specific internal object in a configurable way.
"""

from __future__ import annotations

import collections.abc
import sys
import typing as t
import uuid

from globus_sdk._missing import MISSING, MissingType

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

T = t.TypeVar("T")
R = t.TypeVar("R")

# Omittable[T] means "T may be missing"
# NullableOmittable[T] means "T may be missing or null"
#
# in type systems this kind of construction is sometimes called "Optional" or "Maybe"
# but Python uses "Optional" to mean "T | None" and in the SDK, "None" means "null"
Omittable: TypeAlias[T] = t.Union[T, MissingType]
NullableOmittable: TypeAlias[T] = t.Union[Omittable[T], None]


def stringify(value: NullableOmittable[object]) -> NullableOmittable[str]:
    """
    Convert a value to a string, with handling for None and Missing.

    :param value: The stringifiable object
    """
    if value is None:
        return None
    if value is MISSING:
        return MISSING
    return str(value)


@t.overload
def listify(value: None) -> None: ...
@t.overload
def listify(value: MissingType) -> MissingType: ...
@t.overload
def listify(value: t.Iterable[T]) -> list[T]: ...


def listify(value: NullableOmittable[t.Iterable[T]]) -> NullableOmittable[list[T]]:
    """
    Convert any iterable to a list, with handling for None and Missing.

    :param value: The iterable of objects
    """
    if value is None:
        return None
    if value is MISSING:
        return MISSING
    if isinstance(value, list):
        return value
    return list(value)


def strseq_iter(
    value: t.Iterable[str | uuid.UUID] | str | uuid.UUID,
) -> t.Iterator[str]:
    """
    Iterate over one or more string/string-convertible values.

    :param value: The stringifiable object or objects to iterate over

    This function handles strings, which are themselves iterable,
    by producing the string itself, not it's characters:

    >>> list("foo")
    ['f', 'o', 'o']
    >>> list(strseq_iter("foo"))
    ['foo']

    It also accepts and converts UUIDs and iterables thereof:

    >>> list(strseq_iter(UUID(int=0)))
    ['00000000-0000-0000-0000-000000000000']
    >>> list(strseq_iter([UUID(int=0), UUID(int=1)]))
    ['00000000-0000-0000-0000-000000000000', '00000000-0000-0000-0000-000000000001']

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


@t.overload
def strseq_listify(value: None) -> None: ...
@t.overload
def strseq_listify(value: MissingType) -> MissingType: ...


@t.overload
def strseq_listify(
    value: t.Iterable[str | uuid.UUID] | str | uuid.UUID,
) -> list[str]: ...


def strseq_listify(
    value: NullableOmittable[t.Iterable[str | uuid.UUID] | str | uuid.UUID],
) -> NullableOmittable[list[str]]:
    """
    A wrapper over strseq_iter which produces list outputs.
    This method takes responsibility for checking for MISSING and None values.

    Unlike strseq_iter, this may be the "last mile" remarshalling step before
    data is actually passed to the network layer. Therefore, it makes sense for this
    helper to handle (MISSING | None).

    :param value: The stringifiable object or iterable of objects
    """
    if value is None:
        return None
    if value is MISSING:
        return MISSING
    return list(strseq_iter(value))


@t.overload
def list_map(value: None, mapped_function: t.Callable[[T], R]) -> None: ...


@t.overload
def list_map(
    value: MissingType, mapped_function: t.Callable[[T], R]
) -> MissingType: ...


@t.overload
def list_map(value: t.Iterable[T], mapped_function: t.Callable[[T], R]) -> list[R]: ...


def list_map(
    value: NullableOmittable[t.Iterable[T]], mapped_function: t.Callable[[T], R]
) -> NullableOmittable[list[R]]:
    """
    Like list(map()) but handles None|MISSING.

    :param value: The iterable of objects over which to map
    :param mapped_function: The function to map
    """
    if value is None:
        return None
    if value is MISSING:
        return MISSING
    return [mapped_function(element) for element in value]


@t.overload
def commajoin(value: MissingType) -> MissingType: ...
@t.overload
def commajoin(value: None) -> None: ...
@t.overload
def commajoin(value: str | uuid.UUID | t.Iterable[str | uuid.UUID]) -> str: ...


def commajoin(
    value: NullableOmittable[str | uuid.UUID | t.Iterable[str | uuid.UUID]],
) -> NullableOmittable[str]:
    if value is None:
        return None
    if value is MISSING:
        return MISSING
    # note that this explicit handling of Iterable allows for objects to be
    # passed to this function and be stringified by the `str()` call
    if isinstance(value, collections.abc.Iterable):
        return ",".join(strseq_iter(value))
    return str(value)
