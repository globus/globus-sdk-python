from __future__ import annotations

import sys
import typing as t

from globus_sdk.utils import MISSING

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol


VersionTuple = t.Tuple[int, int, int]

DatatypeCallback = t.Callable[["DocumentWithInducedDatatype"], t.Optional[VersionTuple]]


class DocumentWithInducedDatatype(Protocol):
    DATATYPE_BASE: str
    DATATYPE_VERSION_IMPLICATIONS: dict[str, VersionTuple]
    DATATYPE_VERSION_CALLBACKS: tuple[DatatypeCallback, ...]

    def __contains__(self, key: str) -> bool:  # pragma: no cover
        ...

    def __setitem__(self, key: str, value: t.Any) -> None:  # pragma: no cover
        ...

    def __getitem__(self, key: str) -> t.Any:  # pragma: no cover
        ...


def deduce_datatype_version(obj: DocumentWithInducedDatatype) -> str:
    max_deduced_version = (1, 0, 0)
    for fieldname, version in obj.DATATYPE_VERSION_IMPLICATIONS.items():
        if fieldname not in obj or obj[fieldname] is MISSING:
            continue
        if version > max_deduced_version:
            max_deduced_version = version
    for callback in obj.DATATYPE_VERSION_CALLBACKS:
        opt_version = callback(obj)
        if opt_version is not None and opt_version > max_deduced_version:
            max_deduced_version = opt_version
    return ".".join(str(x) for x in max_deduced_version)


def ensure_datatype(obj: DocumentWithInducedDatatype) -> None:
    if "DATA_TYPE" not in obj or obj["DATA_TYPE"] is MISSING:
        obj["DATA_TYPE"] = f"{obj.DATATYPE_BASE}#{deduce_datatype_version(obj)}"
