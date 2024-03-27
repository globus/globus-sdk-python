from .builder import ScopeBuilder, ScopeBuilderScopes


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
        "manage_projects",
        "view_authentications",
        "view_clients",
        "view_clients_and_scopes",
        "view_consents",
        "view_identities",
        "view_identity_set",
    ],
)
"""Globus Auth scopes.

.. listknownscopes:: globus_sdk.scopes.AuthScopes
    :example_scope: view_identity_set
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
        known_scopes: ScopeBuilderScopes = None,
        known_url_scopes: ScopeBuilderScopes = None,
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
