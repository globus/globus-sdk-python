from typing import Any, Callable, Dict, Optional, Type

from .base import Paginator


def has_paginator(
    paginator_class: Type[Paginator],
    items_key: Optional[str] = None,
    **paginator_params,
):
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
    """

    def decorate(func: Callable):
        func._has_paginator = True  # type: ignore
        func._paginator_class = paginator_class  # type: ignore
        func._paginator_items_key = items_key  # type: ignore
        func._paginator_params = paginator_params  # type: ignore
        func.__doc__ = f"""{func.__doc__}

        **Paginated Usage**

        This method supports paginated access. To use the paginated variant, give the
        same arguments as normal, but prefix the method name with ``paginated``, as in

        >>> client.paginated.{func.__name__}(...)
        """
        return func

    return decorate


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

    Paginators are iterables of response pages, so utlimate usage is like so:

    >>> paginator = client.paginated.foo()  # returns a paginator
    >>> for page in paginator:  # a paginator is an iterable of pages (response objects)
    >>>     print(json.dumps(page.data))  # you can handle each response object in turn

    A ``PaginatorTable`` is built automatically as part of client instantiation.
    Creation of ``PaginatorTable`` objects is considered a private API.
    """

    def __init__(self, client: Any):
        self._client = client
        # _bindings is a lazily loaded table of names -> callables which
        # return paginators
        self._bindings: Dict[str, Callable[..., Paginator]] = {}

    def _add_binding(self, methodname, bound_method):
        paginator_class = bound_method._paginator_class
        paginator_params = bound_method._paginator_params
        paginator_items_key = bound_method._paginator_items_key

        def paginated_method(*args, **kwargs):
            return paginator_class(
                bound_method,
                client_args=args,
                client_kwargs=kwargs,
                items_key=paginator_items_key,
                **paginator_params,
            )

        self._bindings[methodname] = paginated_method

    def __getattr__(self, attrname):
        if attrname not in self._bindings:
            # this could raise AttributeError -- in which case, let it!
            method = getattr(self._client, attrname)
            # not callable -> not a method; not marked paginated -> not relevant
            if not callable(method) or not getattr(method, "_has_paginator", False):
                raise AttributeError(f"'{attrname}' is not a paginated method")

            self._add_binding(attrname, method)

        return self._bindings[attrname]

    # customize pickling methods to ensure that the object is pickle-safe

    def __getstate__(self):
        # when pickling, drop any bound methods
        d = dict(self.__dict__)  # copy
        d["_bindings"] = {}
        return d

    # custom __setstate__ to avoid an infinite loop on `getattr` before `_bindings` is
    # populated
    # see: https://docs.python.org/3/library/pickle.html#object.__setstate__
    def __setstate__(self, d):
        self.__dict__.update(d)
