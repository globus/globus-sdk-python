from __future__ import annotations

import typing as t

import attrs

from globus_sdk import utils


def str_list(
    value: str | t.Iterable[t.Any] | utils.MissingType,
) -> list[str] | utils.MissingType:
    if isinstance(value, utils.MissingType):
        return utils.MISSING
    return list(utils.safe_strseq_iter(value))


nullable_str_list = attrs.converters.optional(str_list)


# use underscore-suffixed names for any conflicts with builtin types, following the
# convention used by sqlalchemy
def list_(
    value: t.Iterable[t.Any] | utils.MissingType,
) -> list[t.Any] | utils.MissingType:
    if isinstance(value, utils.MissingType):
        return utils.MISSING
    return list(value)


nullable_list = attrs.converters.optional(list_)
