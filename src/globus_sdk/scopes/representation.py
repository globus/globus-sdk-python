from __future__ import annotations

import warnings

from ._parser import parse_scope_graph


class Scope:
    """
    A scope object is a representation of a scope which allows modifications to be
    made. In particular, it supports handling scope dependencies via
    ``add_dependency``.

    `str(Scope(...))` produces a valid scope string for use in various methods.

    :param scope_string: The string which will be used as the basis for this Scope
    :param optional: The scope may be marked as optional. This means that the scope can
        be declined by the user without declining consent for other scopes
    """

    def __init__(
        self,
        scope_string: str,
        *,
        optional: bool = False,
        dependencies: list[Scope] | None = None,
    ) -> None:
        if any(c in scope_string for c in "[]* "):
            raise ValueError(
                "Scope instances may not contain the special characters '[]* '. "
                "Use either Scope.deserialize or Scope.parse instead"
            )
        self.scope_string = scope_string
        self.optional = optional
        self.dependencies: list[Scope] = [] if dependencies is None else dependencies

    @staticmethod
    def parse(scope_string: str) -> list[Scope]:
        """
        Parse an arbitrary scope string to a list of scopes.

        Zero or more than one scope may be returned, as in the case of an empty string
        or space-delimited scopes.

        .. warning::

            Parsing passes through an intermediary representation which treats scopes
            as a graph. This ensures that the behavior of parses matches the treatment
            of scope strings in Globus Auth authorization flows.
            However, this also means that the parsing does not allow for strings which
            represent consent trees with structures in which the same scope appears in
            multiple parts of the tree.

        :param scope_string: The string to parse
        """
        scope_graph = parse_scope_graph(scope_string)

        # initialize BFS traversals (one per root node) and copy that data
        # to setup the result data
        bfs_additions: list[Scope] = [
            Scope(s, optional=optional) for s, optional in scope_graph.top_level_scopes
        ]
        results: list[Scope] = list(bfs_additions)

        while bfs_additions:
            current_scope = bfs_additions.pop(0)
            edges = scope_graph.adjacency_matrix[current_scope.scope_string]
            for _, dest, optional in edges:
                dest_scope = Scope(dest, optional=optional)
                current_scope.add_dependency(dest_scope)
                bfs_additions.append(dest_scope)

        return results

    @staticmethod
    def merge_scopes(scopes_a: list[Scope], scopes_b: list[Scope]) -> list[Scope]:
        """
        Given two lists of Scopes, merge them into one list of Scopes by parsing
        them as one combined scope string.

        :param scopes_a: list of Scopes to be merged with scopes_b
        :param scopes_b: list of Scopes to be merged with scopes_a
        """
        # dict of base scope_string: list of scopes with that base scope_string
        return Scope.parse(
            " ".join([str(s) for s in scopes_a] + [str(s) for s in scopes_b])
        )

    @classmethod
    def deserialize(cls, scope_string: str) -> Scope:
        """
        Deserialize a scope string to a scope object.

        This is the special case of parsing in which exactly one scope must be returned
        by the parse. If more than one scope is returned by the parse, a ``ValueError``
        will be raised.

        :param scope_string: The string to parse
        """
        data = Scope.parse(scope_string)
        if len(data) != 1:
            raise ValueError(
                "Deserializing a scope from string did not get exactly one scope. "
                f"Instead got data={data}"
            )
        return data[0]

    def serialize(self) -> str:
        base_scope = ("*" if self.optional else "") + self.scope_string
        if not self.dependencies:
            return base_scope
        return (
            base_scope + "[" + " ".join(c.serialize() for c in self.dependencies) + "]"
        )

    def add_dependency(
        self, scope: str | Scope, *, optional: bool | None = None
    ) -> Scope:
        """
        Add a scope dependency. The dependent scope relationship will be stored in the
        Scope and will be evident in its string representation.

        :param scope: The scope upon which the current scope depends
        :param optional: Mark the dependency an optional one. By default it is not. An
            optional scope dependency can be declined by the user without declining
            consent for the primary scope
        """
        if optional is not None:
            if isinstance(scope, Scope):
                raise ValueError(
                    "cannot use optional=... with a Scope object as the argument to "
                    "add_dependency"
                )
            warnings.warn(
                "Passing 'optional' to add_dependency is deprecated. "
                "Construct an optional Scope object instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            scopeobj = Scope(scope, optional=optional)
        else:
            if isinstance(scope, str):
                scopeobj = Scope.deserialize(scope)
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
        return "Scope(" + ", ".join(parts) + ")"

    def __str__(self) -> str:
        return self.serialize()
