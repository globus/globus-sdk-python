from __future__ import annotations

import typing as t

from .parser import ScopeParser
from .representation import Scope

if t.TYPE_CHECKING:
    from globus_sdk._types import ScopeCollectionType


def scopes_to_str(scopes: ScopeCollectionType) -> str:
    """
    Normalize a scope collection to a space-separated scope string.

    :param scopes: A scope string or object, or an iterable of scope strings or objects.
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


def scopes_to_scope_list(scopes: ScopeCollectionType) -> list[Scope]:
    """
    Normalize a scope collection to a list of Scope objects.

    :param scopes: A scope string or object, or an iterable of scope strings or objects.
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
    obj: ScopeCollectionType,
    *,
    split_root_scopes: bool = True,
) -> t.Iterator[str | Scope]:
    """
    Provide an iterator over a scope collection type, flattening nested scope
    collections as encountered.

    Collections of scope representations are yielded one at a time.
    Individual scope representations are yielded as-is.

    :param obj: A scope collection or scope representation.
    :param iter_scope_strings: If True, scope strings with multiple root scopes are
        split. This flag allows a caller to optimize, skipping a bfs operation if
        merging will be done later purely with strings.

    Example usage:

    .. code-block:: pycon

        >>> list(_iter_scope_collection("foo"))
        ['foo']
        >>> list(_iter_scope_collection(Scope.parse("foo bar"), "baz qux"))
        [Scope('foo'), Scope('bar'), 'baz', 'qux']
        >>> list(_iter_scope_collection("foo bar[baz qux]"))
        ['foo', 'bar[baz qux]']
        >>> list(_iter_scope_collection("foo bar[baz qux]", split_root_scopes=False))
        'foo bar[baz qux]'
    """
    if isinstance(obj, str):
        yield from _iter_scope_string(obj, split_root_scopes)
    elif isinstance(obj, Scope):
        yield obj
    else:
        for item in obj:
            yield from _iter_scope_collection(item, split_root_scopes=split_root_scopes)


def _iter_scope_string(scope_str: str, split_root_scopes: bool) -> t.Iterator[str]:
    if not split_root_scopes or " " not in scope_str:
        yield scope_str

    elif "[" not in scope_str:
        yield from scope_str.split(" ")
    else:
        for scope_obj in ScopeParser.parse(scope_str):
            yield str(scope_obj)
