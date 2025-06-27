"""
The definition of the MISSING sentinel and its type.

These are exposed publicly as `globus_sdk.MISSING` and `globus_sdk.MissingType`.
"""

from __future__ import annotations

import typing as t

T = t.TypeVar("T")

# type checkers don't know that MISSING is a sentinel, so we will describe it
# differently at typing time, allowing for type narrowing on `is MISSING` and
# similar checks
if t.TYPE_CHECKING:
    # pretend that `MISSING: MissingType` is an enum at type-checking time
    #
    # enums are treated as `Literal[...]` values and are narrowed under simple
    # checks, as unions and literal types are
    # therefore, under this definition, `MissingType ~= Literal[MissingType.MISSING]`
    #
    # Therefore, consider this example:
    #
    #       x: int | float | MissingType
    #       if x is not MISSING:
    #           reveal_type(x)
    #
    # This is effectively the same as if we wrote:
    #
    #       x: int | float | Literal["a"]
    #       if x != "a":
    #           reveal_type(x)
    #
    # Both should show `x: int | float`
    import enum

    class MissingType(enum.Enum):
        MISSING = enum.auto()

    MISSING = MissingType.MISSING
else:

    class MissingType:
        def __init__(self) -> None:
            # disable instantiation, but gated to be able to run once
            # when this module is imported
            if "MISSING" in globals():
                raise TypeError("MissingType should not be instantiated")

        def __bool__(self) -> bool:
            return False

        def __copy__(self) -> MissingType:
            return self

        def __deepcopy__(self, memo: dict[int, t.Any]) -> MissingType:
            return self

        # unpickling a MissingType should always return the "MISSING" sentinel
        def __reduce__(self) -> str:
            return "MISSING"

        def __repr__(self) -> str:
            return "<globus_sdk.MISSING>"

    # a sentinel value for "missing" values which are distinguished from `None` (null)
    # this is the default used to indicate that a parameter was not passed, so that
    # method calls passing `None` can be distinguished from those which did not pass any
    # value
    # users should typically not use this value directly, but it is part of the
    # public SDK interfaces along with its type for annotation purposes
    MISSING = MissingType()


@t.overload
def filter_missing(data: dict[str, t.Any]) -> dict[str, t.Any]: ...


@t.overload
def filter_missing(data: None) -> None: ...


def filter_missing(data: dict[str, t.Any] | None) -> dict[str, t.Any] | None:
    if data is None:
        return None
    return {k: v for k, v in data.items() if v is not MISSING}


def none2missing(obj: T | None) -> T | MissingType:
    """
    A converter for interfaces which take "nullable" to mean "omittable", to
    adapt them to usage sites which require use of MISSING for omittable
    elements.

    :param obj: The nullable object to convert to an omittable object.
    """
    if obj is None:
        return MISSING
    return obj
