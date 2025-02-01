from __future__ import annotations

import functools
import inspect
import textwrap
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
    """Resolve a class name to a list of (public) method names + function objects.
    Takes a classname and a list of method names to avoid filtering out.

    :param classname: The name to resolve to a class
    :param include_methods: A list or tuple of method names which would normally be
        excluded as private, but which should be included in the result
    """
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


@functools.lru_cache(maxsize=None)
def read_sphinx_params(docstring: str) -> tuple[str, ...]:
    """
    Given a docstring, extract the `:param:` declarations into a tuple of strings.

    :param docstring: The ``__doc__`` to parse, as it appeared on the original object

    Params start with `:param ...` and end
    - at the end of the string
    - at the next param
    - when a non-indented, non-param line is found

    Whitespace lines within a param doc are supported.

    All produced param strings are dedented.
    """
    docstring = textwrap.dedent(docstring)

    result: list[str] = []
    current: list[str] = []
    for line in docstring.splitlines():
        if not current:
            if line.startswith(":param"):
                current = [line]
            else:
                continue
        else:
            # a new param -- flush the current one and restart
            if line.startswith(":param"):
                result.append("\n".join(current).strip())
                current = [line]
            # a continuation line for the current param (indented)
            # or a blank line -- it *could* be a continuation of param doc (include it)
            elif line != line.lstrip() or not line:
                current.append(line)
            # otherwise this is a populated line, not indented, and without a `:param`
            # start -- stop looking for more param doc
            else:
                break
    if current:
        result.append("\n".join(current).strip())

    return tuple(result)
