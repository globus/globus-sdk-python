from __future__ import annotations

import datetime
import typing as t
import uuid

if t.TYPE_CHECKING:
    from globus_sdk.scopes import MutableScope
    from globus_sdk.scopes.scope_definition import Scope

# these types are aliases meant for internal use
IntLike = t.Union[int, str]
UUIDLike = t.Union[uuid.UUID, str]
DateLike = t.Union[str, datetime.datetime]

ScopeCollectionType = t.Union[
    str,
    "Scope",
    "MutableScope",
    t.Iterable[str],
    t.Iterable["Scope"],
    t.Iterable["MutableScope"],
    t.Iterable[t.Union[str, "Scope", "MutableScope"]],
    t.Iterable[t.Union[str, "Scope"]],
    t.Iterable[t.Union[str, "MutableScope"]],
    t.Iterable[t.Union["Scope", "MutableScope"]],
]
