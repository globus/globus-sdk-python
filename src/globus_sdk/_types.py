from __future__ import annotations

import datetime
import sys
import typing as t
import uuid

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol

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


class ResponseLike(Protocol):
    @property
    def http_status(self) -> int:
        ...

    @property
    def http_reason(self) -> str:
        ...

    @property
    def headers(self) -> t.Mapping[str, str]:
        ...

    @property
    def content_type(self) -> str | None:
        ...

    @property
    def text(self) -> str:
        ...

    @property
    def binary_content(self) -> bytes:
        ...
