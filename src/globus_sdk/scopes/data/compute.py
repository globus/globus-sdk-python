from __future__ import annotations

from ..builder import ScopeBuilder, ScopeBuilderScopes


class _ComputeScopeBuilder(ScopeBuilder):
    """The Compute service breaks the scopes/resource server convention: its resource
    server is a service name and its scopes are built around the client ID.
    """

    def __init__(
        self,
        resource_server: str,
        client_id: str,
        known_scopes: ScopeBuilderScopes = None,
        known_url_scopes: ScopeBuilderScopes = None,
    ) -> None:
        self._client_id = client_id
        super().__init__(
            resource_server,
            known_scopes=known_scopes,
            known_url_scopes=known_url_scopes,
        )

    def urn_scope_string(self, scope_name: str) -> str:
        return f"urn:globus:auth:scope:{self._client_id}:{scope_name}"

    def url_scope_string(self, scope_name: str) -> str:
        return f"https://auth.globus.org/scopes/{self._client_id}/{scope_name}"


ComputeScopes = _ComputeScopeBuilder(
    "funcx_service",
    "facd7ccc-c5f4-42aa-916b-a0e270e2c2a9",
    known_url_scopes=["all"],
)
