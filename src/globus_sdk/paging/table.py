from __future__ import annotations

import typing as t

from globus_sdk.response import GlobusHTTPResponse

from .base import Paginator

C = t.TypeVar("C", bound=t.Callable[..., GlobusHTTPResponse])


class PaginatorTable:
    """
    A PaginatorTable maps multiple methods of an SDK client to paginated variants.
    Given a method, client.foo annotated with the `has_paginator` decorator, the table
    will gain a function attribute `foo` (name matching is automatic) which returns a
    Paginator.

    Clients automatically build and attach paginator tables under the ``paginated``
    attribute.
    That is, if `client` has two methods `foo` and `bar` which are marked as paginated,
    that will let us call

    >>> client.paginated.foo()
    >>> client.paginated.bar()

    where ``client.paginated`` is a ``PaginatorTable``.

    Paginators are iterables of response pages, so ultimate usage is like so:

    >>> paginator = client.paginated.foo()  # returns a paginator
    >>> for page in paginator:  # a paginator is an iterable of pages (response objects)
    >>>     print(json.dumps(page.data))  # you can handle each response object in turn

    A ``PaginatorTable`` is built automatically as part of client instantiation.
    Creation of ``PaginatorTable`` objects is considered a private API.
    """

    def __init__(self, client: t.Any):
        self._client = client
        # _bindings is a lazily loaded table of names -> callables which
        # return paginators
        self._bindings: dict[str, t.Callable[..., Paginator[t.Any]]] = {}

    def _add_binding(
        self, methodname: str, bound_method: t.Callable[..., t.Any]
    ) -> None:
        self._bindings[methodname] = Paginator.wrap(bound_method)

    def __getattr__(self, attrname: str) -> t.Callable[..., Paginator[t.Any]]:
        if attrname not in self._bindings:
            # this could raise AttributeError -- in which case, let it!
            method = getattr(self._client, attrname)
            try:
                self._bindings[attrname] = Paginator.wrap(method)
            # ValueError is raised if the method being wrapped is not paginated
            except ValueError as e:
                raise AttributeError(f"'{attrname}' is not a paginated method") from e

        return self._bindings[attrname]

    # customize pickling methods to ensure that the object is pickle-safe

    def __getstate__(self) -> dict[str, t.Any]:
        # when pickling, drop any bound methods
        d = dict(self.__dict__)  # copy
        d["_bindings"] = {}
        return d

    # custom __setstate__ to avoid an infinite loop on `getattr` before `_bindings` is
    # populated
    # see: https://docs.python.org/3/library/pickle.html#object.__setstate__
    def __setstate__(self, d: dict[str, t.Any]) -> None:
        self.__dict__.update(d)
