from ..collection import StaticScopeCollection, _urn_scope
from ..representation import Scope


class _AuthScopes(StaticScopeCollection):
    resource_server = "auth.globus.org"

    openid = Scope("openid")
    email = Scope("email")
    profile = Scope("profile")

    manage_projects = _urn_scope(resource_server, "manage_projects")
    view_authentications = _urn_scope(resource_server, "view_authentications")
    view_clients = _urn_scope(resource_server, "view_clients")
    view_clients_and_scopes = _urn_scope(resource_server, "view_clients_and_scopes")
    view_consents = _urn_scope(resource_server, "view_consents")
    view_identities = _urn_scope(resource_server, "view_identities")
    view_identity_set = _urn_scope(resource_server, "view_identity_set")


AuthScopes = _AuthScopes()
