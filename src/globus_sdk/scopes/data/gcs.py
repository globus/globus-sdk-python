from functools import cached_property

from ..collection import DynamicScopeCollection, _url_scope, _urn_scope
from ..representation import Scope


class GCSEndpointScopes(DynamicScopeCollection):
    """
    A dynamic ScopeCollection with a named property for the GCS
    manage_collections scope. "manage_collections" is a scope on GCS Endpoints.
    The resource_server string should be the GCS Endpoint ID.

    **Examples**

    >>> sc = GCSEndpointScopes("xyz")
    >>> mc_scope = sb.manage_collections
    """

    _scope_names = ("manage_collections",)

    @cached_property
    def manage_collections(self) -> Scope:
        return _urn_scope(self.resource_server, "manage_collections")


class GCSCollectionScopes(DynamicScopeCollection):
    """
    A dynamic ScopeCollection with a named property for the GCS data_access scope.
    "data_access" is a scope on GCS Collections. The resource_server string should
    be the GCS Collection ID.

    **Examples**

    >>> sc = GCSCollectionScopes("xyz")
    >>> da_scope = sc.data_access
    >>> https_scope = sc.https
    """

    _scope_names = ("data_access", "https")

    @cached_property
    def data_access(self) -> Scope:
        return _url_scope(self.resource_server, "data_access")

    @cached_property
    def https(self) -> Scope:
        return _url_scope(self.resource_server, "https")
