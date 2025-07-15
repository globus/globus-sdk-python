from __future__ import annotations

import typing as t

from .parser import ScopeParser
from .representation import Scope


def scopes_to_str(scopes: str | Scope | t.Iterable[str | Scope]) -> str:
    """
    Normalize scopes to a space-separated scope string.

    :param scopes: A scope string, scope object, or an iterable of scope strings
        and scope objects.
    :returns: A space-separated scope string.

    Example usage:

    .. code-block:: pycon

        >>> scopes_to_str(Scope("foo"))
        'foo'
        >>> scopes_to_str(Scope("foo"), "bar", Scope("qux"))
        'foo bar qux'
    """
    scope_iter = _iter_scope_collection(scopes, split_root_scopes=False)
    return " ".join(str(scope) for scope in scope_iter)


def scopes_to_scope_list(scopes: str | Scope | t.Iterable[str | Scope]) -> list[Scope]:
    """
    Normalize scopes to a list of Scope objects.

    :param scopes: A scope string, scope object, or an iterable of scope strings
        and scope objects.
    :returns: A list of Scope objects.

    Example usage:

    .. code-block:: pycon

        >>> scopes_to_scope_list(Scope("foo"))
        [Scope('foo')]
        >>> scopes_to_scope_list(Scope("foo"), "bar baz", Scope("qux"))
        [Scope('foo'), Scope('bar'), Scope('baz'), Scope('qux')]
    """
    scope_list: list[Scope] = []
    for scope in _iter_scope_collection(scopes):
        if isinstance(scope, str):
            scope_list.extend(ScopeParser.parse(scope))
        else:
            scope_list.append(scope)
    return scope_list


def _iter_scope_collection(
    obj: str | Scope | t.Iterable[str | Scope],
    *,
    split_root_scopes: bool = True,
) -> t.Iterator[str | Scope]:
    """
    Provide an iterator over a collection of scopes.

    Collections of scope representations are yielded one at a time.
    Individual scope representations are yielded as-is.

    :param obj: A scope string, scope object, or an iterable of scope strings
        and scope objects.
    :param split_root_scopes: If True, scope strings with multiple root scopes are
        split. This flag allows a caller to optimize, skipping a bfs operation if
        merging will be done later purely with strings.

    Example usage:

    .. code-block:: pycon

        >>> list(_iter_scope_collection("foo"))
        ['foo']
        >>> list(_iter_scope_collection(Scope.parse("foo bar") + ["baz qux"]))
        [Scope('foo'), Scope('bar'), 'baz', 'qux']
        >>> list(_iter_scope_collection("foo bar[baz qux]"))
        ['foo', 'bar[baz qux]']
        >>> list(_iter_scope_collection("foo bar[baz qux]", split_root_scopes=False))
        ['foo bar[baz qux]']
    """
    if isinstance(obj, str):
        yield from _iter_scope_string(obj, split_root_scopes)
    elif isinstance(obj, Scope):
        yield obj
    else:
        yield from _iter_scope_iterable(obj, split_root_scopes)


def _iter_scope_string(scope_str: str, split_root_scopes: bool) -> t.Iterator[str]:
    if not split_root_scopes or " " not in scope_str:
        yield scope_str

    elif "[" not in scope_str:
        yield from scope_str.split(" ")
    else:
        for scope_obj in ScopeParser.parse(scope_str):
            yield str(scope_obj)


def _iter_scope_iterable(
    scope_iterable: t.Iterable[str | Scope], split_root_scopes: bool
) -> t.Iterator[str | Scope]:
    for scope in scope_iterable:
        if isinstance(scope, str):
            yield from _iter_scope_string(scope, split_root_scopes)
        elif isinstance(scope, Scope):
            yield scope
        else:
            raise TypeError(f"Expected str or Scope in iterable, got {type(scope)}")
