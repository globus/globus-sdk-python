# test that the internal _guards module provides valid and well-formed type-guards
import typing as t

from globus_sdk import _guards


def get_any() -> t.Any:
    return 1


x = get_any()
t.assert_type(x, t.Any)

# test reduce().apply
if _guards.reduce(str).apply(x):
    y1 = x
    t.assert_type(y1, str)

# test is_list_of / reduce().list_of
if _guards.is_list_of(x, str):
    t.assert_type(x, list[str])
elif _guards.is_list_of(x, int):
    t.assert_type(x, list[int])

if _guards.reduce(str).list_of(x):
    t.assert_type(x, list[str])
elif _guards.reduce(int).list_of(x):
    t.assert_type(x, list[int])

# test is_optional / reduce().optional
if _guards.is_optional(x, float):
    t.assert_type(x, float | None)
elif _guards.is_optional(x, bytes):
    t.assert_type(x, bytes | None)

if _guards.reduce(float).optional(x):
    t.assert_type(x, float | None)
elif _guards.reduce(bytes).optional(x):
    t.assert_type(x, bytes | None)


# test is_optional_list_of / reduce().optional_list
if _guards.is_optional_list_of(x, type(None)):
    t.assert_type(x, list[None] | None)
elif _guards.is_optional_list_of(x, dict):
    t.assert_type(x, list[dict[t.Any, t.Any]] | None)

if _guards.reduce(type(None)).optional_list(x):
    t.assert_type(x, list[None] | None)
elif _guards.reduce(dict).optional_list(x):
    t.assert_type(x, list[dict[t.Any, t.Any]] | None)
