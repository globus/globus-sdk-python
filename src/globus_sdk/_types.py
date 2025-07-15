from __future__ import annotations

import datetime
import typing as t
import uuid

# these types are aliases meant for internal use
IntLike = t.Union[int, str]
UUIDLike = t.Union[uuid.UUID, str]
DateLike = t.Union[str, datetime.datetime]


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
