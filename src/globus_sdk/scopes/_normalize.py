from __future__ import annotations

import typing as t

from .representation import Scope
from .scope_definition import MutableScope

if t.TYPE_CHECKING:
    from globus_sdk._types import ScopeCollectionType


def scopes_to_str(scopes: ScopeCollectionType) -> str:
    """
    Utility function to normalize a scope collection to a space-separated scope string.

    e.g., scopes_to_str(Scope("foo")) -> "foo"
    e.g., scopes_to_str(Scope("foo"), "bar", MutableScope("qux")) -> "foo bar qux"

    :param scopes: A scope string or object, or an iterable of scope strings or objects.
    :returns: A space-separated scope string.
    """
    scope_iter = _iter_scope_collection(scopes, split_root_scopes=False)
    return " ".join(str(scope) for scope in scope_iter)


def scopes_to_scope_list(scopes: ScopeCollectionType) -> list[Scope]:
    """
    Utility function to normalize a scope collection to a list of Scope objects.

    :param scopes: A scope string or object, or an iterable of scope strings or objects.
    :returns: A list of Scope objects.
    """
    scope_list: list[Scope] = []
    for scope in _iter_scope_collection(scopes, split_root_scopes=True):
        if isinstance(scope, str):
            scope_list.extend(Scope.parse(scope))
        elif isinstance(scope, MutableScope):
            scope_list.extend(Scope.parse(str(scope)))
        else:
            scope_list.append(scope)
    return scope_list


def _iter_scope_collection(
    obj: ScopeCollectionType,
    split_root_scopes: bool,
) -> t.Iterator[str | MutableScope | Scope]:
    """
    Convenience function to iterate over a scope collection type.

    Collections of scope representations are yielded one at a time.
    Individual scope representations are yielded as-is.

    :obj: A scope collection or scope representation.
    :iter_scope_strings: If True, scope strings with multiple root scopes are split.
        This flag allows you to skip a bfs operation if merging can be done purely
        with strings.
        e.g., _iter_scope_collection("foo bar[baz qux]", True) -> "foo", "bar[baz qux]"
        e.g., _iter_scope_collection("foo bar[baz qux]", False) -> "foo bar[baz qux]"
    """
    if isinstance(obj, str):
        yield from _iter_scope_string(obj, split_root_scopes)
    elif isinstance(obj, MutableScope) or isinstance(obj, Scope):
        yield obj
    else:
        for item in obj:
            yield from _iter_scope_collection(item, split_root_scopes)


def _iter_scope_string(scope_str: str, split_root_scopes: bool) -> t.Iterator[str]:
    if not split_root_scopes or " " not in scope_str:
        yield scope_str

    elif "[" not in scope_str:
        yield from scope_str.split(" ")
    else:
        for scope_obj in Scope.parse(scope_str):
            yield str(scope_obj)
