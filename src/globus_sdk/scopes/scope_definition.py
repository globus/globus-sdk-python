"""
This defines the Scope object and the scope parser.
Because these components are mutually dependent, it's easiest if they're kept in a
single module.
"""
from __future__ import annotations

import enum
import typing as t
import warnings

from globus_sdk._types import ScopeCollectionType


class ScopeParseError(ValueError):
    pass


def _iter_scope_collection(obj: ScopeCollectionType) -> t.Iterator[str]:
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, Scope):
        yield str(obj)
    elif isinstance(obj, MutableScope):
        yield str(obj)
    else:
        for item in obj:
            yield str(item)


class ParseTokenType(enum.Enum):
    # a string like 'urn:globus:auth:scopes:transfer.api.globus.org:all'
    scope_string = enum.auto()
    # the optional marker, '*'
    opt_marker = enum.auto()
    # '[' and ']'
    lbracket = enum.auto()
    rbracket = enum.auto()


class ParseToken:
    def __init__(self, value: str, token_type: ParseTokenType) -> None:
        self.value = value
        self.token_type = token_type


def _tokenize(scope_string: str) -> list[ParseToken]:
    tokens: list[ParseToken] = []
    current_token: list[str] = []
    for idx, c in enumerate(scope_string):
        try:
            peek: str | None = scope_string[idx + 1]
        except IndexError:
            peek = None

        if c in "[]* ":
            if current_token:
                tokens.append(
                    ParseToken("".join(current_token), ParseTokenType.scope_string)
                )
                current_token = []

            if c == "*":
                if peek == " ":
                    raise ScopeParseError("'*' must not be followed by a space")
                tokens.append(ParseToken(c, ParseTokenType.opt_marker))
            elif c == "[":
                tokens.append(ParseToken(c, ParseTokenType.lbracket))
            elif c == "]":
                if peek is not None and peek not in (" ", "]"):
                    raise ScopeParseError("']' may only be followed by a space or ']'")
                tokens.append(ParseToken(c, ParseTokenType.rbracket))
            elif c == " ":
                if peek == "[":
                    raise ScopeParseError("'[' cannot have a preceding space")
            else:
                raise NotImplementedError
        else:
            current_token.append(c)
    if current_token:
        tokens.append(ParseToken("".join(current_token), ParseTokenType.scope_string))
    return tokens


def _parse_tokens(tokens: list[ParseToken]) -> list[Scope]:
    # value to return
    ret: list[Scope] = []
    # track whether or not the current scope is optional (has a preceding *)
    current_optional = False
    # keep a stack of "parents", each time we enter a `[` context, push the last scope
    # and each time we exit via a `]`, pop from the stack
    parents: list[Scope] = []
    # track the current (or, by similar terminology, "last") complete scope seen
    current_scope: Scope | None = None

    for idx in range(len(tokens)):
        token = tokens[idx]
        try:
            peek: ParseToken | None = tokens[idx + 1]
        except IndexError:
            peek = None

        if token.token_type == ParseTokenType.opt_marker:
            current_optional = True
            if peek is None:
                raise ScopeParseError("ended in optional marker")
            if peek.token_type != ParseTokenType.scope_string:
                raise ScopeParseError(
                    "a scope string must always follow an optional marker"
                )

        elif token.token_type == ParseTokenType.lbracket:
            if peek is None:
                raise ScopeParseError("ended in left bracket")
            if peek.token_type == ParseTokenType.rbracket:
                raise ScopeParseError("found empty brackets")
            if peek.token_type == ParseTokenType.lbracket:
                raise ScopeParseError("found double left-bracket")
            if not current_scope:
                raise ScopeParseError("found '[' without a preceding scope string")

            parents.append(current_scope)
        elif token.token_type == ParseTokenType.rbracket:
            if not parents:
                raise ScopeParseError("found ']' with no matching '[' preceding it")
            parents.pop()
        else:
            current_scope = Scope(token.value, optional=current_optional)
            current_optional = False
            if parents:
                parents[-1].dependencies.append(current_scope)
            else:
                ret.append(current_scope)
    if parents:
        raise ScopeParseError("unclosed brackets, missing ']'")

    return ret


class Scope:
    """
    A scope object is a representation of a scope which allows modifications to be
    made. In particular, it supports handling scope dependencies via
    ``add_dependency``.

    `str(Scope(...))` produces a valid scope string for use in various methods.

    :param scope_string: The string which will be used as the basis for this Scope
    :type scope_string: str
    :param optional: The scope may be marked as optional. This means that the scope can
        be declined by the user without declining consent for other scopes
    :type optional: bool
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
        """
        tokens = _tokenize(scope_string)
        return _parse_tokens(tokens)

    @classmethod
    def deserialize(cls, scope_string: str) -> Scope:
        """
        Deserialize a scope string to a scope object.

        This is the special case of parsing in which exactly one scope must be returned
        by the parse.
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
        :type scope: str
        :param optional: Mark the dependency an optional one. By default it is not. An
            optional scope dependency can be declined by the user without declining
            consent for the primary scope
        :type optional: bool, optional
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

    def _contains(self, other: t.Any) -> bool:
        """
        .. warning::

            The ``_contains`` method is a non-authoritative convenience for comparing
            parsed scopes. Although the essence and intent of the check is summarized
            below, there is no guarantee that it correctly reflects the permissions of a
            token or tokens. The structure of the data for a given consent in Globus
            Auth is not perfectly reflected in the parse tree.

        ``in`` and ``not in`` are defined as permission coverage checks

        ``scope1 in scope2`` means that a token scoped for
        ``scope2`` has all of the permissions of a token scoped for ``scope1``.

        A scope is covered by another scope if

        - the top level strings match
        - the optional-ness matches OR only the covered scope is optional
        - the dependencies of the covered scope are all covered by dependencies of
          the covering scope

        Therefore, the following are true:

        .. code-block:: pycon

            >>> s = lambda x: Scope.deserialize(x)  # define this for brevity below
            # self inclusion works, including when optional
            >>> s("foo")._contains(s("foo"))
            >>> s("*foo")._contains(s("*foo"))
            # an optional scope is covered by a non-optional one, but not the reverse
            >>> not s("foo")._contains(s("*foo"))
            >>> s("*foo")._contains(s("foo"))
            # dependencies have the expected meanings
            >>> s("foo")._contains(s("foo[bar]"))
            >>> not s("foo[bar]")._contains(s("foo"))
            >>> s("foo[bar]")._contains(s("foo[bar[baz]]"))
            # dependencies are not transitive and obey "optionalness" matching
            >>> not s("foo[bar]")._contains(s("foo[fizz[bar]]"))
            >>> not s("foo[bar]")._contains(s("foo[*bar]"))
        """
        # scopes can only contain other scopes
        if not isinstance(other, Scope):
            return False

        # top-level scope must match
        if self.scope_string != other.scope_string:
            return False

        # between self.optional and other.optional, there are four possibilities,
        # of which three are acceptable and one is not
        # both optional and neither optional are okay,
        # 'self' being non-optional and 'other' being optional is okay
        # the failing case is 'other in self' when 'self' is optional and 'other' is not
        #
        #    self.optional | other.optional | (other in self) is possible
        #    --------------|----------------|----------------------------
        #        true      |    true        |    true
        #        false     |    false       |    true
        #        false     |    true        |    true
        #        true      |    false       |    false
        #
        # so only check for that one case
        if self.optional and not other.optional:
            return False

        # dependencies must all be contained -- search for a contrary example
        for other_dep in other.dependencies:
            for dep in self.dependencies:
                if dep._contains(other_dep):
                    break
            # reminder: the else branch of a for-else means that the break was never hit
            else:
                return False

        # all criteria were met -- True!
        return True

    @staticmethod
    def scopes2str(obj: ScopeCollectionType) -> str:
        """
        Given a scope string, a collection of scope strings, a Scope object, a
        collection of Scope objects, or a mixed collection of strings and
        Scopes, convert to a string which can be used in a request.
        """
        return " ".join(_iter_scope_collection(obj))


# TODO: convert MutableScope into an alias of Scope
class MutableScope:
    """
    A scope object is a representation of a scope which allows modifications to be
    made. In particular, it supports handling scope dependencies via
    ``add_dependency``.

    `str(MutableScope(...))` produces a valid scope string for use in various methods.

    :param scope_string: The string which will be used as the basis for this Scope
    :type scope_string: str
    :param optional: The scope may be marked as optional. This means that the scope can
        be declined by the user without declining consent for other scopes
    :type optional: bool
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
        :type scope: str
        :param optional: Mark the dependency an optional one. By default it is not. An
            optional scope dependency can be declined by the user without declining
            consent for the primary scope
        :type optional: bool, optional
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
        """
        return " ".join(_iter_scope_collection(obj))
