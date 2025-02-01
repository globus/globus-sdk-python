from __future__ import annotations

import inspect
import types
import typing as t
from pydoc import locate


def locate_class(classname: str) -> type:
    cls = locate(classname)
    if not inspect.isclass(cls):
        raise RuntimeError(
            f"uh-oh, {classname} is not a class name? type(classname)={type(cls)}"
        )
    return cls


def classname2methods(
    classname: str, include_methods: t.Sequence[str]
) -> list[tuple[str, types.FunctionType]]:
    """resolve a class name to a list of (public) method names
    takes a classname and a list of method names to avoid filtering out"""
    cls = locate_class(classname)

    # get methods of the object as [(name, <unbound method>), ...]
    methods = inspect.getmembers(cls, predicate=inspect.isfunction)

    def methodname_is_good(m: str) -> bool:
        if m in include_methods:
            return True
        # filter out dunder-methods and `_private` methods
        if m.startswith("_"):
            return False
        # filter out any inherited methods which are not overloaded
        if m not in cls.__dict__:
            return False
        return True

    return [(name, value) for name, value in methods if methodname_is_good(name)]


def derive_doc_url_base(service: str | None) -> str:
    if service is None:
        return "https://docs.globus.org/api"
    elif service == "groups":
        return "https://groups.api.globus.org/redoc#operation"
    elif service == "gcs":
        return "https://docs.globus.org/globus-connect-server/v5/api"
    elif service == "flows":
        return "https://globusonline.github.io/globus-flows#tag"
    elif service == "compute":
        return "https://compute.api.globus.org/redoc#tag"
    else:
        raise ValueError(f"Unsupported extdoclink service '{service}'")
