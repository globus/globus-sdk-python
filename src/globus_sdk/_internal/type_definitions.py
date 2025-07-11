from __future__ import annotations

import datetime
import typing as t
import uuid

if t.TYPE_CHECKING:
    from globus_sdk.scopes import Scope


# these types are aliases meant for internal use
IntLike = t.Union[int, str]
UUIDLike = t.Union[uuid.UUID, str]
DateLike = t.Union[str, datetime.datetime]

ScopeCollectionType = t.Union[
    str,
    "Scope",
    t.Iterable["ScopeCollectionType"],
]


class ResponseLike(t.Protocol):
    @property
    def http_status(self) -> int: ...

    @property
    def http_reason(self) -> str: ...

    @property
    def headers(self) -> t.Mapping[str, str]: ...

    @property
    def content_type(self) -> str | None: ...

    @property
    def text(self) -> str: ...

    @property
    def binary_content(self) -> bytes: ...
