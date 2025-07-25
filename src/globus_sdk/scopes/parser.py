from __future__ import annotations

import typing as t

from globus_sdk import exc

from ._graph_parser import ScopeGraph
from .representation import Scope


class ScopeParser:
    """
    The ``ScopeParser`` handles the conversion of strings to scopes.

    Most interfaces are classmethods, meaning users should prefer usage like
    ``ScopeParser.parse("foo")``
    """

    @classmethod
    def parse(cls, scope_string: str) -> list[Scope]:
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
        # build the graph intermediate representation
        scope_graph = ScopeGraph.parse(scope_string)

        # traverse the graph in a reversed BFS scan
        #
        # this means we'll handle leaf nodes first, and we'll never reach a
        # node before its descendants (dependencies)
        #
        # as we work, build a lookup table for built Scope objects so that we can
        # quickly retrieve elements
        built_scopes: dict[tuple[str, bool], Scope] = {}

        for name, optionality in list(scope_graph.breadth_first_walk())[::-1]:
            dependencies: tuple[Scope, ...] = tuple(
                # the lookup in built_scopes here is safe because of the
                # reversed BFS ordering
                built_scopes[(dep_name, dep_optional)]
                for _, dep_name, dep_optional in scope_graph.adjacency_matrix[name]
            )

            built_scopes[(name, optionality)] = Scope(
                name, optional=optionality, dependencies=dependencies
            )

        # only return the top-level elements from that build process
        # (the roots of the forest-shaped graph)
        return [built_scopes[key] for key in scope_graph.top_level_scopes]

    @classmethod
    def merge_scopes(cls, scopes_a: list[Scope], scopes_b: list[Scope]) -> list[Scope]:
        """
        Given two lists of Scopes, merge them into one list of Scopes by parsing
        them as one combined scope string.

        :param scopes_a: list of Scopes to be merged with scopes_b
        :param scopes_b: list of Scopes to be merged with scopes_a
        """
        # dict of base scope_string: list of scopes with that base scope_string
        return cls.parse(
            " ".join([str(s) for s in scopes_a] + [str(s) for s in scopes_b])
        )

    @classmethod
    def serialize(
        cls, scopes: str | Scope | t.Iterable[str | Scope], *, reject_empty: bool = True
    ) -> str:
        """
        Normalize scopes to a space-separated scope string.

        The results of this method are suitable for sending to Globus Auth.
        Scopes are not parsed, merged, or normalized by this method.

        :param scopes: A scope string, scope object, or an iterable of scope strings
            and scope objects.
        :param reject_empty: When true (the default), raise an error if the
            scopes serialize to the empty string.
        :returns: A space-separated scope string.

        Example usage:

        .. code-block:: pycon

            >>> ScopeParser.serialize([Scope("foo"), "bar", Scope("qux")])
            'foo bar qux'
        """
        scope_iter: t.Iterable[str | Scope]
        if isinstance(scopes, (str, Scope)):
            scope_iter = (scopes,)
        else:
            scope_iter = scopes

        result = " ".join(str(scope) for scope in scope_iter)
        if reject_empty and result == "":
            raise exc.GlobusSDKUsageError(
                "'scopes' cannot be the empty string or empty collection."
            )
        return result
