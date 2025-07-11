# test that the internal guards module provides valid and well-formed type-guards
import typing as t

from globus_sdk._internal import guards


def get_any() -> t.Any:
    return 1


x = get_any()
t.assert_type(x, t.Any)

# test is_list_of
if guards.is_list_of(x, str):
    t.assert_type(x, list[str])
elif guards.is_list_of(x, int):
    t.assert_type(x, list[int])

# test is_optional
if guards.is_optional(x, float):
    t.assert_type(x, float | None)
elif guards.is_optional(x, bytes):
    t.assert_type(x, bytes | None)


# test is_optional_list_of
if guards.is_optional_list_of(x, type(None)):
    t.assert_type(x, list[None] | None)
elif guards.is_optional_list_of(x, dict):
    t.assert_type(x, list[dict[t.Any, t.Any]] | None)
