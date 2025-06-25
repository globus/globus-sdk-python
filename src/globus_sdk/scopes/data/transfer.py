from ..collection import StaticScopeCollection, _urn_scope


class _TransferScopes(StaticScopeCollection):
    resource_server = "transfer.api.globus.org"

    all = _urn_scope(resource_server, "all")
    gcp_install = _urn_scope(resource_server, "gcp_install")


TransferScopes = _TransferScopes()
