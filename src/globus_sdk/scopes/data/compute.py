from ..collection import StaticScopeCollection, _url_scope


class _ComputeScopes(StaticScopeCollection):
    # The Compute service breaks the scopes/resource server convention: its resource
    # server is a service name and its scopes are built around the client ID.
    resource_server = "funcx_service"
    client_id = "facd7ccc-c5f4-42aa-916b-a0e270e2c2a9"

    all = _url_scope(client_id, "all")


ComputeScopes = _ComputeScopes()
