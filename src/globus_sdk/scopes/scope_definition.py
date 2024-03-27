"""
THIS IS A LEGACY MODULE

This module defines a legacy scope object and parser called `MutableScope`.
It is maintained for backwards compatibility.

For new code, use the `globus_sdk.Scope` object.
"""

from __future__ import annotations

import typing as t
import warnings

if t.TYPE_CHECKING:
    from globus_sdk._types import ScopeCollectionType


def _iter_scope_collection(obj: ScopeCollectionType) -> t.Iterator[str]:
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, MutableScope):
        yield str(obj)
    else:
        for item in obj:
            yield str(item)


class MutableScope:
    """
    A scope object is a representation of a scope which allows modifications to be
    made. In particular, it supports handling scope dependencies via
    ``add_dependency``.

    `str(MutableScope(...))` produces a valid scope string for use in various methods.

    :param scope_string: The string which will be used as the basis for this Scope
    :param optional: The scope may be marked as optional. This means that the scope can
        be declined by the user without declining consent for other scopes
    """

    def __init__(
        self,
        scope_string: str,
        *,
        optional: bool = False,
        dependencies: list[MutableScope] | None = None,
    ) -> None:
        if any(c in scope_string for c in "[]* "):
            raise ValueError(
                "MutableScope instances may not contain the special characters '[]* '."
            )
        self.scope_string = scope_string
        self.optional = optional
        self.dependencies: list[MutableScope] = (
            [] if dependencies is None else dependencies
        )

    def serialize(self) -> str:
        base_scope = ("*" if self.optional else "") + self.scope_string
        if not self.dependencies:
            return base_scope
        return (
            base_scope + "[" + " ".join(c.serialize() for c in self.dependencies) + "]"
        )

    def add_dependency(
        self,
        scope: str | MutableScope,
        *,
        optional: bool | None = None,
    ) -> MutableScope:
        """
        Add a scope dependency. The dependent scope relationship will be stored in the
        Scope and will be evident in its string representation.

        :param scope: The scope upon which the current scope depends
        :param optional: Mark the dependency an optional one. By default it is not. An
            optional scope dependency can be declined by the user without declining
            consent for the primary scope
        """
        if optional is not None:
            if isinstance(scope, MutableScope):
                raise ValueError(
                    "cannot use optional=... with a MutableScope object as the "
                    "argument to add_dependency"
                )
            warnings.warn(
                "Passing 'optional' to add_dependency is deprecated. "
                "Construct an optional MutableScope object instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            scopeobj = MutableScope(scope, optional=optional)
        else:
            if isinstance(scope, str):
                scopeobj = MutableScope(scope)
            else:
                scopeobj = scope
        self.dependencies.append(scopeobj)
        return self

    def __repr__(self) -> str:
        parts: list[str] = [f"'{self.scope_string}'"]
        if self.optional:
            parts.append("optional=True")
        if self.dependencies:
            parts.append(f"dependencies={self.dependencies!r}")
        return "MutableScope(" + ", ".join(parts) + ")"

    def __str__(self) -> str:
        return self.serialize()

    @staticmethod
    def scopes2str(obj: ScopeCollectionType) -> str:
        """
        Given a scope string, a collection of scope strings, a MutableScope object, a
        collection of MutableScope objects, or a mixed collection of strings and
        Scopes, convert to a string which can be used in a request.

        :param obj: The object or collection to convert to a string
        """
        return " ".join(_iter_scope_collection(obj))
