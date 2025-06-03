from __future__ import annotations

import dataclasses
import warnings


@dataclasses.dataclass(slots=True)
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

    scope_string: str
    optional: bool = dataclasses.field(default=False)
    dependencies: list[Scope] = dataclasses.field(default_factory=list)

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
                scopeobj = Scope.parse(scope)
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
        base_scope = ("*" if self.optional else "") + self.scope_string
        if not self.dependencies:
            return base_scope
        return base_scope + "[" + " ".join(str(c) for c in self.dependencies) + "]"
