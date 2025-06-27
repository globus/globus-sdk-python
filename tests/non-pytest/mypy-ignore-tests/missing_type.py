import typing as t

from globus_sdk import MISSING, MissingType

# first, the type of `MISSING` must be `MissingType`
t.assert_type(MISSING, MissingType)

# second, a variable annotated as `int | MissingType` is assignable with `MISSING`
x: int | MissingType = MISSING

# and `MissingType` is not the same as None, Ellipsis, False, 0, or other weirdness
# these error!
y: MissingType
y = None  # type: ignore[assignment]
y = Ellipsis  # type: ignore[assignment]
y = ...  # type: ignore[assignment]
y = False  # type: ignore[assignment]
y = 0  # type: ignore[assignment]

# given that x is int|MissingType, `x is not MISSING` should narrow to `int`
if x is not MISSING:
    t.assert_type(x, int)
else:
    # don't do this:
    #   t.assert_type(x, MissingType)
    # although that looks right, `MissingType` != `Literal[MISSING]`, so it fails
    # (at least on some mypy versions)
    # instead, confirm that `not isinstance(x, MissingType)` narrows to a Never
    if not isinstance(x, MissingType):  # noqa: SDK003
        t.assert_never(x)
