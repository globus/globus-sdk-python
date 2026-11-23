# this script must run in an environment where the SDK is installed
#
# usage: tox r -e check-paginated-docs

import inspect
import types
import typing as t

import globus_sdk


def main() -> None:
    failures = []
    for client_type, methodname, func in all_paginated_methods():
        if not pagination_is_documented(func):
            failures.append((client_type, methodname))

    if failures:
        for client_type, methodname in failures:
            print(
                "paginted method was not documented: "
                f"{client_type.__name__}.{methodname}"
            )
        raise SystemExit(1)


def pagination_is_documented(func: types.FunctionType) -> bool:
    # any paginated method MUST document paginated usage in the tab-set
    return ".. tab-item:: Paginated Usage" in func.__doc__


def all_paginated_methods() -> (
    t.Iterator[tuple[type[globus_sdk.BaseClient], str, types.FunctionType]]
):
    for client_type in all_client_types():
        for methodname, func in iter_paginated_methods(client_type):
            yield client_type, methodname, func


def all_client_types() -> t.Iterator[type[globus_sdk.BaseClient]]:
    for name in dir(globus_sdk):
        obj = getattr(globus_sdk, name)
        if (
            isinstance(obj, type)
            and issubclass(obj, globus_sdk.BaseClient)
            and obj is not globus_sdk.BaseClient
        ):
            yield obj


def iter_paginated_methods(
    client_type: type[globus_sdk.BaseClient],
) -> t.Iterator[tuple[str, types.FunctionType]]:
    for methodname, func in iter_public_methods(client_type):
        if getattr(func, "_has_paginator", False):
            yield methodname, func


def iter_public_methods(
    client_type: type[globus_sdk.BaseClient],
) -> t.Iterator[tuple[str, types.FunctionType]]:
    methods = inspect.getmembers(client_type, predicate=inspect.isfunction)
    for methodname, func in methods:
        # skip private methods
        if methodname.startswith("_"):
            continue
        # skip inherited methods
        if methodname not in client_type.__dict__:
            continue
        yield methodname, func


if __name__ == "__main__":
    main()
