from ..builder import ScopeBuilder


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
