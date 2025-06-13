"""
The definition of the MISSING sentinel and its type.

These are exposed publicly as `globus_sdk.MISSING` and `globus_sdk.MissingType`.
"""

from __future__ import annotations

import typing as t


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
# users should typically not use this value directly, but it is part of the public SDK
# interfaces along with its type for annotation purposes
#
# *new in version 3.30.0*
MISSING = MissingType()


@t.overload
def filter_missing(data: dict[str, t.Any]) -> dict[str, t.Any]: ...


@t.overload
def filter_missing(data: None) -> None: ...


def filter_missing(data: dict[str, t.Any] | None) -> dict[str, t.Any] | None:
    if data is None:
        return None
    return {k: v for k, v in data.items() if v is not MISSING}
