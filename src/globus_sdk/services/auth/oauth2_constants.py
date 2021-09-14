from globus_sdk.scopes import AuthScopes, TransferScopes

__all__ = ["DEFAULT_REQUESTED_SCOPES"]

DEFAULT_REQUESTED_SCOPES = (
    AuthScopes.openid,
    AuthScopes.profile,
    AuthScopes.email,
    TransferScopes.all,
)
