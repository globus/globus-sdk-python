"""
This defines the Scope object and the scope parser.
Because these components are mutually dependent, it's easiest if they're kept in a
single module.
"""
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


def _tokenize(scope_string: str) -> t.List[ParseToken]:
    tokens: t.List[ParseToken] = []
    current_token: t.List[str] = []
    for c in scope_string:
        if c in "[]* ":
            if current_token:
                tokens.append(
                    ParseToken("".join(current_token), ParseTokenType.scope_string)
                )
                current_token = []
            if c == "*":
                tokens.append(ParseToken(c, ParseTokenType.opt_marker))
            elif c == "[":
                tokens.append(ParseToken(c, ParseTokenType.lbracket))
            elif c == "]":
                tokens.append(ParseToken(c, ParseTokenType.rbracket))
            elif c == " ":
                if tokens and tokens[-1].token_type == ParseTokenType.opt_marker:
                    raise ScopeParseError(
                        "optional marker must not be followed by a space"
                    )
            else:
                raise NotImplementedError
        else:
            current_token.append(c)
    if current_token:
        tokens.append(ParseToken("".join(current_token), ParseTokenType.scope_string))
    return tokens


def _parse_tokens(tokens: t.List[ParseToken]) -> t.List["Scope"]:
    # value to return
    ret: t.List[Scope] = []
    # track whether or not the current scope is optional (has a preceding *)
    current_optional = False
    # keep a stack of "parents", each time we enter a `[` context, push the last scope
    # and each time we exit via a `]`, pop from the stack
    parents: t.List[Scope] = []
    # track the current (or, by similar terminology, "last") complete scope seen
    current_scope: t.Optional[Scope] = None

    for idx in range(len(tokens)):
        token = tokens[idx]
        try:
            peek: t.Optional[ParseToken] = tokens[idx + 1]
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
    A mutable scope is a representation of a scope which allows modifications to be
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
        dependencies: t.Optional[t.List["Scope"]] = None,
    ) -> None:
        if any(c in scope_string for c in "[]* "):
            raise ValueError(
                "Scope instances may not contain the special characters '[]* '. "
                "Use either Scope.deserialize or Scope.parse instead"
            )
        self._scope_string = scope_string
        self.optional = optional
        self.dependencies: t.List[Scope] = [] if dependencies is None else dependencies

    @staticmethod
    def parse(scope_string: str) -> t.List["Scope"]:
        """
        Parse an arbitrary scope string to a list of scopes.

        Zero or more than one scope may be returned, as in the case of an empty string
        or space-delimited scopes.
        """
        tokens = _tokenize(scope_string)
        return _parse_tokens(tokens)

    @classmethod
    def deserialize(cls, scope_string: str) -> "Scope":
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
        base_scope = ("*" if self.optional else "") + self._scope_string
        if not self.dependencies:
            return base_scope
        return (
            base_scope + "[" + " ".join(c.serialize() for c in self.dependencies) + "]"
        )

    def add_dependency(
        self, scope: t.Union[str, "Scope"], *, optional: t.Optional[bool] = None
    ) -> "Scope":
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
        parts: t.List[str] = [f"'{self._scope_string}'"]
        if self.optional:
            parts.append("optional=True")
        if self.dependencies:
            parts.append(f"dependencies={self.dependencies!r}")
        return "Scope(" + ", ".join(parts) + ")"

    def __str__(self) -> str:
        return self.serialize()

    def __contains__(self, other: t.Any) -> bool:
        """
        scope1 in scope2 is defined as subtree matching.

        A scope contains another scope if
        - the top level strings match
        - the optional-ness matches OR only the contained scope is optional
        - the dependencies of the contained scope are all contained in dependencies of
          the containing scope

        Therefore, the following are true:

        .. code-block:: pycon

            # self inclusion works
            >>> Scope.deserialize("foo") in Scope.deserialize("foo")
            # optional mismatches in either direction do not indicate containment
            >>> Scope.deserialize("foo") not in Scope.deserialize("*foo")
            >>> Scope.deserialize("*foo") not in Scope.deserialize("foo")
            # dependencies have the expected meanings
            >>> Scope.deserialize("foo") in Scope.deserialize("foo[bar]")
            >>> Scope.deserialize("foo[bar]") not in Scope.deserialize("foo")
            >>> Scope.deserialize("foo[bar]") in Scope.deserialize("foo[bar[baz]]")
            # dependencies are not transitive and obey "optionalness" matching
            >>> Scope.deserialize("foo[bar]") not in Scope.deserialize("foo[fizz[bar]]")
            >>> Scope.deserialize("foo[bar]") not in Scope.deserialize("foo[*bar]")
        """
        # scopes can only contain other scopes
        if not isinstance(other, Scope):
            return False

        # top-level scope must match
        if self._scope_string != other._scope_string:
            return False
        # if both are optional, okay
        # if neither is optional, okay
        # but if only one is optional...
        if self.optional != other.optional:
            # ... then make sure it is 'other'
            if self.optional:
                return False

        # dependencies must all be contained -- search for a contrary example
        for other_dep in other.dependencies:
            found_match = False
            for dep in self.dependencies:
                if other_dep in dep:
                    found_match = True
                    break
            if not found_match:
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