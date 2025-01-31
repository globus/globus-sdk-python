from ..builder import ScopeBuilder

SearchScopes = ScopeBuilder(
    "search.api.globus.org",
    known_scopes=[
        "all",
        "globus_connect_server",
        "ingest",
        "search",
    ],
)
