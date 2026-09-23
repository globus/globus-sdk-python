from __future__ import annotations

import abc
import functools
import inspect
import typing as t

from globus_sdk.response import GlobusHTTPResponse

PageT = t.TypeVar("PageT", bound=GlobusHTTPResponse)
P = t.ParamSpec("P")
R = t.TypeVar("R", bound=GlobusHTTPResponse)
C = t.TypeVar("C", bound=t.Callable[..., GlobusHTTPResponse])


# stub for mypy
class _PaginatedFunc(t.Generic[PageT]):
    _has_paginator: bool
    _paginator_class: type[Paginator[PageT]]
    _paginator_items_key: str | None
    _paginator_params: dict[str, t.Any]


class Paginator(t.Iterable[PageT], metaclass=abc.ABCMeta):
    """
    Base class for all paginators.
    This guarantees is that they have generator methods named ``pages`` and ``items``.

    Iterating on a Paginator is equivalent to iterating on its ``pages``.

    :param method: A bound method of an SDK client, used to generate a paginated variant
    :param items_key: The key to use within pages of results to get an array of items
    :param client_args: Arguments to the underlying method which are passed when the
        paginator is instantiated. i.e. given ``client.paginated.foo(a, b, c=1)``, this
        will be ``(a, b)``. The paginator will pass these arguments to each call of the
        bound method as it pages.
    :param client_kwargs: Keyword arguments to the underlying method, like
        ``client_args`` above. ``client.paginated.foo(a, b, c=1)`` will pass this as
        ``{"c": 1}``. As with ``client_args``, it's passed to each paginated call.
    """

    # the arguments which must be supported on the paginated method in order
    # for the paginator to pass them
    _REQUIRES_METHOD_KWARGS: tuple[str, ...] = ()

    def __init__(
        self,
        method: t.Callable[..., t.Any],
        *,
        items_key: str | None = None,
        client_args: tuple[t.Any, ...],
        client_kwargs: dict[str, t.Any],
        # the Base paginator must accept arbitrary additional kwargs to indicate that
        # its child classes could define and use additional kwargs
        **kwargs: t.Any,
    ) -> None:
        self.method = method
        self.items_key = items_key
        self.client_args = client_args
        self.client_kwargs = client_kwargs

    def __iter__(self) -> t.Iterator[PageT]:
        yield from self.pages()

    @abc.abstractmethod
    def pages(self) -> t.Iterator[PageT]:
        """``pages()`` yields GlobusHTTPResponse objects, each one representing a page
        of results."""

    def items(self) -> t.Iterator[t.Any]:
        """
        ``items()`` of a paginator is a generator which yields each item in each page of
        results.

        ``items()`` may raise a ``ValueError`` if the paginator was constructed without
        identifying a key for use within each page of results. This may be the case for
        paginators whose pages are not primarily an array of data.
        """
        if self.items_key is None:
            raise ValueError(
                "Cannot provide items() iteration on a paginator where 'items_key' "
                "is not set."
            )
        for page in self.pages():
            yield from page[self.items_key]

    @classmethod
    def wrap(cls, method: t.Callable[P, R]) -> t.Callable[P, Paginator[R]]:
        """
        This is an alternate method for getting a paginator for a paginated method which
        correctly preserves the type signature of the paginated method.

        It should be used on instances of clients and only passed bound methods of those
        clients. For example, given usage

            >>> tc = TransferClient()
            >>> paginator = tc.paginated.endpoint_search(...)

        a well-typed paginator can be acquired with

            >>> tc = TransferClient()
            >>> paginated_call = Paginator.wrap(tc.endpoint_search)
            >>> paginator = paginated_call(...)

        Although the syntax is slightly more verbose, this allows `mypy` and other type
        checkers to more accurately infer the type of the paginator.

        :param method: The method to convert to a paginator
        """
        if not inspect.ismethod(method):
            raise TypeError(f"Paginator.wrap can only be used on methods, not {method}")
        if not getattr(method, "_has_paginator", False):
            raise ValueError(f"'{method}' is not a paginated method")

        as_paginated = t.cast(_PaginatedFunc[PageT], method)
        paginator_class = as_paginated._paginator_class
        paginator_params = as_paginated._paginator_params
        paginator_items_key = as_paginated._paginator_items_key

        @functools.wraps(method)
        def paginated_method(*args: t.Any, **kwargs: t.Any) -> Paginator[PageT]:
            return paginator_class(
                method,
                client_args=tuple(args),
                client_kwargs=kwargs,
                items_key=paginator_items_key,
                **paginator_params,
            )

        return t.cast(t.Callable[P, Paginator[R]], paginated_method)


def has_paginator(
    paginator_class: type[Paginator[PageT]],
    items_key: str | None = None,
    **paginator_params: t.Any,
) -> t.Callable[[C], C]:
    """
    Mark a callable -- typically a client method -- as having pagination parameters.
    Usage:

    >>> class MyClient(BaseClient):
    >>>     @has_paginator(MarkerPaginator)
    >>>     def foo(...): ...

    This will mark ``MyClient.foo`` as paginated with marker style pagination.
    It will then be possible to get a paginator for ``MyClient.foo`` via

    >>> c = MyClient(...)
    >>> paginator = c.paginated.foo()

    :param paginator_class: The type of paginator used by this method
    :param items_key: The key to use within pages of results to get an array of items
    :param paginator_params: Additional parameters to pass to the paginator constructor
    """

    def decorate(func: C) -> C:
        as_paginated = t.cast(_PaginatedFunc[PageT], func)
        as_paginated._has_paginator = True
        as_paginated._paginator_class = paginator_class
        as_paginated._paginator_items_key = items_key
        as_paginated._paginator_params = paginator_params
        return func

    return decorate
