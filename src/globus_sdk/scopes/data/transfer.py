from ..builder import ScopeBuilder

TransferScopes = ScopeBuilder(
    "transfer.api.globus.org",
    known_scopes=[
        "all",
        "gcp_install",
    ],
)
