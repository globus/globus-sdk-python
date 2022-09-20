from typing import Dict, Iterable, Iterator, List, Tuple, Union

from globus_sdk import utils

# this type alias is meant for internal use, which is why it's named with an underscore
_ScopeCollectionType = Union[
    str,
    "MutableScope",
    Iterable[str],
    Iterable["MutableScope"],
    Iterable[Union[str, "MutableScope"]],
]


def _iter_scope_collection(obj: _ScopeCollectionType) -> Iterator[str]:
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, MutableScope):
        yield str(obj)
    else:
        for item in obj:
            yield str(item)


class MutableScope:
    """
    A mutable scope is a representation of a scope which allows modifications to be
    made. In particular, it supports handling scope dependencies via
    ``add_dependency``. A MutableScope can be created

    `str(MutableScope(...))` produces a valid scope string for use in various methods.

    :param scope_string: The scope which will be used as the basis for this MutableScope
    :type scope_string: str
    :param optional: The scope may be marked as optional. This means that the scope can
        be declined by the user without declining consent for other scopes
    :type optional: bool
    """

    def __init__(self, scope_string: str, *, optional: bool = False) -> None:
        self.optional = optional
        self._scope_string = scope_string
        # map from scope name to optional=t/f
        # this means that dependencies are not ordered, but that adding the same
        # dependency twice is a no-op
        self._dependencies: Dict[str, bool] = {}

    def add_dependency(self, scope: str, *, optional: bool = False) -> "MutableScope":
        """
        Add a scope dependency. The dependent scope relationship will be stored in the
        MutableScope and will be evident in its string representation.

        :param scope: The scope upon which the current scope depends
        :type scope: str
        :param optional: Mark the dependency an optional one. By default it is not. An
            optional scope dependency can be declined by the user without declining
            consent for the primary scope
        :type optional: bool, optional
        """
        if scope.startswith("*"):
            raise ValueError(
                "Scope strings for add_dependency cannot contain a leading '*'. "
                "To pass an optional scope, first strip any leading '*', and use "
                "'optional=True' if the scope must be marked optional."
            )
        self._dependencies[scope] = optional
        return self

    def __repr__(self) -> str:
        parts: List[str] = [f"'{self._scope_string}'"]
        if self.optional:
            parts.append("optional=True")
        if self._dependencies:
            parts.append(f"dependencies={self._dependencies}")
        return "MutableScope(" + ", ".join(parts) + ")"

    def _formatted_dependencies(self) -> Iterator[str]:
        for scope in self._dependencies:
            optional_prefix = "*" if self._dependencies[scope] else ""
            yield optional_prefix + scope

    def __str__(self) -> str:
        base_scope = ("*" if self.optional else "") + self._scope_string
        if not self._dependencies:
            return base_scope
        return base_scope + "[" + " ".join(self._formatted_dependencies()) + "]"

    @staticmethod
    def scopes2str(obj: _ScopeCollectionType) -> str:
        """
        Given a scope string, a collection of scope strings, a MutableScope object, a
        collection of MutableScope objects, or a mixed collection of strings and
        MutableScopes, convert to a string which can be used in a request.
        """
        return " ".join(_iter_scope_collection(obj))


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

    _classattr_scope_names: List[str] = []

    def __init__(
        self,
        resource_server: str,
        *,
        known_scopes: Union[List[str], str, None] = None,
        known_url_scopes: Union[List[str], str, None] = None,
    ) -> None:
        self.resource_server = resource_server
        self._known_scopes = (
            list(utils.safe_strseq_iter(known_scopes))
            if known_scopes is not None
            else []
        )
        self._known_url_scopes = (
            list(utils.safe_strseq_iter(known_url_scopes))
            if known_url_scopes is not None
            else []
        )
        self._known_scope_names: List[str] = []
        if self._known_scopes:
            for scope_name in self._known_scopes:
                self._known_scope_names.append(scope_name)
                setattr(self, scope_name, self.urn_scope_string(scope_name))
        if self._known_url_scopes:
            for scope_name in self._known_url_scopes:
                self._known_scope_names.append(scope_name)
                setattr(self, scope_name, self.url_scope_string(scope_name))

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
        raise AttributeError

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

    def make_mutable(self, scope: str) -> MutableScope:
        """
        For a given scope, create a MutableScope object.

        The ``scope`` name given refers to the name of a scope attached to the
        ScopeBuilder. It is given by attribute name, not by the full scope string.

        **Examples**

        Using the ``TransferScopes`` object, one could reference ``all`` as follows:

        >>> TransferScopes.all
        'urn:globus:auth:scope:transfer.api.globus.org:all'
        >>> TransferScopes.make_mutable("all")
        MutableScope('urn:globus:auth:scope:transfer.api.globus.org:all')

        This is equivalent to constructing a MutableScope object from the resolved
        scope string, as in

        >>> MutableScope(TransferScopes.all)
        MutableScope('urn:globus:auth:scope:transfer.api.globus.org:all')

        :param scope: The name of the scope to convert to a MutableScope
        :type scope: str
        """
        return MutableScope(getattr(self, scope))

    def _iter_scopes(self) -> Iterator[Tuple[str, str]]:
        for name in self._classattr_scope_names:
            yield (name, getattr(self, name))
        for name in self._known_scope_names:
            yield (name, getattr(self, name))

    def __str__(self) -> str:
        return f"ScopeBuilder[{self.resource_server}]\n" + "\n".join(
            f"  {k}:\n    {v}" for k, v in self._iter_scopes()
        )


class GCSEndpointScopeBuilder(ScopeBuilder):
    """
    A ScopeBuilder with a named property for the GCS manage_collections scope.
    "manage_collections" is a scope on GCS Endpoints. The resource_server string should
    be the GCS Endpoint ID.

    **Examples**

    >>> sb = GCSEndpointScopeBuilder("xyz")
    >>> mc_scope = sb.manage_collections
    """

    _classattr_scope_names = ["manage_collections"]

    @property
    def manage_collections(self) -> str:
        return self.urn_scope_string("manage_collections")


class GCSCollectionScopeBuilder(ScopeBuilder):
    """
    A ScopeBuilder with a named property for the GCS data_access scope.
    "data_access" is a scope on GCS Collections. The resource_server string should
    be the GCS Collection ID.

    **Examples**

    >>> sb = GCSCollectionScopeBuilder("xyz")
    >>> da_scope = sb.data_access
    >>> https_scope = sb.https
    """

    _classattr_scope_names = ["data_access", "https"]

    @property
    def data_access(self) -> str:
        return self.url_scope_string("data_access")

    @property
    def https(self) -> str:
        return self.url_scope_string("https")


class _AuthScopesBuilder(ScopeBuilder):
    _classattr_scope_names = ["openid", "email", "profile"]

    openid: str = "openid"
    email: str = "email"
    profile: str = "profile"


AuthScopes = _AuthScopesBuilder(
    "auth.globus.org",
    known_scopes=[
        "view_authentications",
        "view_clients",
        "view_clients_and_scopes",
        "view_identities",
        "view_identity_set",
    ],
)
"""Globus Auth scopes.

.. listknownscopes:: globus_sdk.scopes.AuthScopes
    add_scopes=openid,email,profile
    example_scope=view_identity_set
"""


class _FlowsScopeBuilder(ScopeBuilder):
    """
    The Flows Service breaks the scopes/resource server convention:
      its resource server is a domain name but its scopes are built around the client id
    Given that there isn't a simple way to support this more generally
      (and we shouldn't encourage supporting this more generally), this class serves to
      build out the scopes accurately specifically for Flows
    """

    def __init__(
        self,
        domain_name: str,
        client_id: str,
        known_scopes: Union[List[str], str, None] = None,
        known_url_scopes: Union[List[str], str, None] = None,
    ) -> None:
        self._client_id = client_id
        super().__init__(
            domain_name, known_scopes=known_scopes, known_url_scopes=known_url_scopes
        )

    def urn_scope_string(self, scope_name: str) -> str:
        return f"urn:globus:auth:scope:{self._client_id}:{scope_name}"

    def url_scope_string(self, scope_name: str) -> str:
        return f"https://auth.globus.org/scopes/{self._client_id}/{scope_name}"


FlowsScopes = _FlowsScopeBuilder(
    "flows.globus.org",
    "eec9b274-0c81-4334-bdc2-54e90e689b9a",
    known_url_scopes=[
        "manage_flows",
        "view_flows",
        "run",
        "run_status",
        "run_manage",
    ],
)
"""Globus Flows scopes.
.. listknownscopes:: globus_sdk.scopes.FlowsScopes
"""


GroupsScopes = ScopeBuilder(
    "groups.api.globus.org",
    known_scopes=[
        "all",
        "view_my_groups_and_memberships",
    ],
)
"""Groups scopes.

.. listknownscopes:: globus_sdk.scopes.GroupsScopes
"""


NexusScopes = ScopeBuilder(
    "nexus.api.globus.org",
    known_scopes=[
        "groups",
    ],
)
"""Nexus scopes (internal use only).

.. listknownscopes:: globus_sdk.scopes.NexusScopes
"""

SearchScopes = ScopeBuilder(
    "search.api.globus.org",
    known_scopes=[
        "all",
        "globus_connect_server",
        "ingest",
        "search",
    ],
)
"""Globus Search scopes.

.. listknownscopes:: globus_sdk.scopes.SearchScopes
"""

TimerScopes = ScopeBuilder(
    "524230d7-ea86-4a52-8312-86065a9e0417",
    known_url_scopes=[
        "timer",
    ],
)
"""Globus Timer scopes.
.. listknownscopes:: globus_sdk.scopes.TimerScopes
"""

TransferScopes = ScopeBuilder(
    "transfer.api.globus.org",
    known_scopes=[
        "all",
        "gcp_install",
    ],
)
"""Globus Transfer scopes.

.. listknownscopes:: globus_sdk.scopes.TransferScopes
"""
