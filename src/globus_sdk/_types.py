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
    t.Iterable[str],
    t.Iterable["Scope"],
    t.Iterable[t.Union[str, "Scope"]],
]
