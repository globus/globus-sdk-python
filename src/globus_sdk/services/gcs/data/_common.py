import sys
import typing as t

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol


class DocumentWithInducedDatatype(Protocol):
    DATATYPE_BASE: str
    DATATYPE_VERSION_IMPLICATIONS: t.Dict[str, t.Tuple[int, int, int]]

    def __contains__(self, key: str) -> bool:  # pragma: no cover
        ...

    def __setitem__(self, key: str, value: t.Any) -> None:  # pragma: no cover
        ...


def deduce_datatype_version(obj: DocumentWithInducedDatatype) -> str:
    max_deduced_version = (1, 0, 0)
    for fieldname, version in obj.DATATYPE_VERSION_IMPLICATIONS.items():
        if fieldname not in obj:
            continue
        if version > max_deduced_version:
            max_deduced_version = version
    return ".".join(str(x) for x in max_deduced_version)


def ensure_datatype(obj: DocumentWithInducedDatatype) -> None:
    if "DATA_TYPE" not in obj:
        obj["DATA_TYPE"] = f"{obj.DATATYPE_BASE}#{deduce_datatype_version(obj)}"
