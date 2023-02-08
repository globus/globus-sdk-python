from __future__ import annotations

import typing as t

from .scope_definition import MutableScope

ScopeBuilderScopes = t.Union[
    None,
    str,
    t.Tuple[str, str],
    t.List[t.Union[str, t.Tuple[str, str]]],
]


class ScopeBuilder:
    """
    Utility class for creating scope strings for a specified resource server.

    :param resource_server: The identifier, usually a domain name or a UUID, for the
        resource server to return scopes for.
    :type resource_server: str
    :param known_scopes: A list of scope names to pre-populate on this instance. This
        will set attributes on the instance using the URN scope format.
    :type known_scopes: list of str, optional
    :param known_url_scopes: A list of scope names to pre-populate on this instance.
        This will set attributes on the instance using the URL scope format.
    :type known_url_scopes: list of str, optional
    """

    _classattr_scope_names: list[str] = []

    def __init__(
        self,
        resource_server: str,
        *,
        known_scopes: ScopeBuilderScopes = None,
        known_url_scopes: ScopeBuilderScopes = None,
    ) -> None:
        self.resource_server = resource_server

        self._registered_scope_names: list[str] = []
        self._register_scopes(known_scopes, self.urn_scope_string)
        self._register_scopes(known_url_scopes, self.url_scope_string)

    def _register_scopes(
        self, scopes: ScopeBuilderScopes, transform_func: t.Callable[[str], str]
    ) -> None:
        scopes_dict = self._scopes_input_to_dict(scopes)
        for scope_name, scope_val in scopes_dict.items():
            self._registered_scope_names.append(scope_name)
            setattr(self, scope_name, transform_func(scope_val))

    def _scopes_input_to_dict(self, items: ScopeBuilderScopes) -> dict[str, str]:
        """
        ScopeBuilders accepts many collection-style types of scopes. This function
          normalizes all of those types into a standard {scope_name: scope_val} dict

        Translation Map:
        None => {}
        "my-str" => {"my-str": "my-str"}
        ["my-list"] => {"my-list": "my-list"}
        ("my-tuple-key", "my-tuple-val") => {"my-tuple-key": "my-tuple-val"}
        """
        if items is None:
            return {}
        elif isinstance(items, str):
            return {items: items}
        elif isinstance(items, tuple):
            return {items[0]: items[1]}
        else:
            items_dict = {}
            for item in items:
                if isinstance(item, str):
                    items_dict[item] = item
                else:
                    items_dict[item[0]] = item[1]
            return items_dict

    @property
    def scope_names(self) -> list[str]:
        return self._classattr_scope_names + self._registered_scope_names

    # custom __getattr__ instructs `mypy` that unknown attributes of a ScopeBuilder are
    # of type `str`, allowing for dynamic attribute names
    # to test, try creating a module with
    #
    #       from globus_sdk.scopes import TransferScopes
    #       x = TransferScopes.all
    #
    # without this method, the assignment to `x` would fail type checking
    # because `all` is unknown to mypy
    #
    # note that the implementation just raises AttributeError; this is okay because
    # __getattr__ is only called as a last resort, when __getattribute__ has failed
    # normal attribute access will not be disrupted
    def __getattr__(self, name: str) -> str:
        raise AttributeError(f"Unrecognized Attribute '{name}'")

    def urn_scope_string(self, scope_name: str) -> str:
        """
        Return a complete string representing the scope with a given name for this
        client, in the Globus Auth URN format.

        Note that this module already provides many such scope strings for use with
        Globus services.

        **Examples**

        >>> sb = ScopeBuilder("transfer.api.globus.org")
        >>> sb.urn_scope_string("transfer.api.globus.org", "all")
        "urn:globus:auth:scope:transfer.api.globus.org:all"

        :param scope_name: The short name for the scope involved.
        :type scope_name: str
        """
        return f"urn:globus:auth:scope:{self.resource_server}:{scope_name}"

    def url_scope_string(self, scope_name: str) -> str:
        """
        Return a complete string representing the scope with a given name for this
        client, in URL format.

        **Examples**

        >>> sb = ScopeBuilder("actions.globus.org")
        >>> sb.url_scope_string("actions.globus.org", "hello_world")
        "https://auth.globus.org/scopes/actions.globus.org/hello_world"

        :param scope_name: The short name for the scope involved.
        :type scope_name: str
        """
        return f"https://auth.globus.org/scopes/{self.resource_server}/{scope_name}"

    def make_mutable(self, scope: str, *, optional: bool = False) -> MutableScope:
        """
        For a given scope, create a MutableScope object.

        The ``scope`` name given refers to the name of a scope attached to the
        ScopeBuilder. It is given by attribute name, not by the full scope string.

        **Examples**

        Using the ``TransferScopes`` object, one could reference ``all`` as follows:

        >>> TransferScopes.all
        'urn:globus:auth:scope:transfer.api.globus.org:all'
        >>> TransferScopes.make_mutable("all")
        Scope('urn:globus:auth:scope:transfer.api.globus.org:all')

        This is equivalent to constructing a Scope object from the resolved
        scope string, as in

        >>> Scope(TransferScopes.all)
        Scope('urn:globus:auth:scope:transfer.api.globus.org:all')

        :param scope: The name of the scope to convert to a MutableScope
        :type scope: str
        :param optional: If true, the created MutableScope object will be marked
            optional
        :type optional: bool
        """
        return MutableScope(getattr(self, scope), optional=optional)

    def __str__(self) -> str:
        return f"ScopeBuilder[{self.resource_server}]\n" + "\n".join(
            f"  {name}:\n    {getattr(self, name)}" for name in self.scope_names
        )
