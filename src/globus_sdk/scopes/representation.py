from __future__ import annotations

import dataclasses
import sys
import typing as t

# pass slots=True on 3.10+
# it's not strictly necessary, but it improves performance
if sys.version_info >= (3, 10):
    _add_dataclass_kwargs = {"slots": True}
else:
    _add_dataclass_kwargs = {}


@dataclasses.dataclass(frozen=True, repr=False, **_add_dataclass_kwargs)
class Scope:
    """
    A scope object is a representation of a scope and its dynamic dependencies
    (other scopes).

    A scope also has optionality, also called its "atomically revovocable" setting.
    An optional scope can be revoked without revoking consent for other scopes
    which were granted at the same time.

    Scopes are immutable, and provide several evolver methods which produce new
    Scopes. In particular, ``with_dependency`` and ``with_dependencies`` create
    new scopes with added dependencies.

    ``str(Scope(...))`` produces a valid scope string for use in various methods.

    :param scope_string: The string which will be used as the basis for this Scope
    :param optional: The scope may be marked as optional. This means that the scope can
        be declined by the user without declining consent for other scopes.
    """

    scope_string: str
    optional: bool = dataclasses.field(default=False)
    dependencies: tuple[Scope, ...] = dataclasses.field(default=())

    def __post_init__(
        self,
    ) -> None:
        if any(c in self.scope_string for c in "[]* "):
            raise ValueError(
                "Scope instances may not contain the special characters '[]* '. "
                "Use Scope.parse instead."
            )

    @classmethod
    def parse(cls, scope_string: str) -> Scope:
        """
        Deserialize a scope string to a scope object.

        This is the special case of parsing in which exactly one scope must be returned
        by the parse. If more than one scope is returned by the parse, a ``ValueError``
        will be raised.

        :param scope_string: The string to parse
        """
        # deferred import because ScopeParser depends on Scope, but Scope.parse
        # is a wrapper over ScopeParser.parse()
        from .parser import ScopeParser

        data = ScopeParser.parse(scope_string)
        if len(data) != 1:
            raise ValueError(
                "`Scope.parse()` did not get exactly one scope. "
                f"Instead got data={data}"
            )
        return data[0]

    def with_dependency(self, other_scope: Scope) -> Scope:
        """
        Create a new scope with a dependency.
        The dependent scope relationship will be stored in the Scope and will
        be evident in its string representation.

        :param other_scope: The scope upon which the current scope depends.
        """
        return dataclasses.replace(
            self, dependencies=self.dependencies + (other_scope,)
        )

    def with_dependencies(self, other_scopes: t.Iterable[Scope]) -> Scope:
        """
        Create a new scope with added dependencies.
        The dependent scope relationships will be stored in the Scope and will
        be evident in its string representation.

        :param other_scopes: The scopes upon which the current scope depends.
        """
        return dataclasses.replace(
            self, dependencies=self.dependencies + tuple(other_scopes)
        )

    def with_optional(self, optional: bool) -> Scope:
        """
        Create a new scope with a different 'optional' value.

        :param optional: Whether or not the scope is optional.
        """
        return dataclasses.replace(self, optional=optional)

    def __repr__(self) -> str:
        parts: list[str] = [f"'{self.scope_string}'"]
        if self.optional:
            parts.append("optional=True")
        if self.dependencies:
            parts.append(f"dependencies={self.dependencies!r}")
        return "Scope(" + ", ".join(parts) + ")"

    def __str__(self) -> str:
        base_scope = ("*" if self.optional else "") + self.scope_string
        if not self.dependencies:
            return base_scope
        return base_scope + "[" + " ".join(str(c) for c in self.dependencies) + "]"
