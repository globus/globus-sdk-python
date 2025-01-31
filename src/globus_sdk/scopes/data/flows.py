from __future__ import annotations

import typing as t

from globus_sdk._types import UUIDLike

from ..builder import ScopeBuilder, ScopeBuilderScopes


class _FlowsScopeBuilder(ScopeBuilder):
    """
    The Flows service breaks the scopes/resource server convention: its resource server
    is a domain name but its scopes are built around the client ID.

    Given that there isn't a simple way to support this more generally (and we
    shouldn't encourage supporting this more generally), this class serves to
    build out the scopes accurately specifically for Flows.
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
        "all",
        "manage_flows",
        "view_flows",
        "run",
        "run_status",
        "run_manage",
    ],
)


class _SpecificFlowScopesClassStub(ScopeBuilder):
    """
    This stub object ensures that the type deductions for type checkers (e.g. mypy) on
    SpecificFlowClient.scopes are correct.

    Primarily, it should be possible to access the `scopes` attribute, the `user`
    scope, and the `resource_server`, but these usages should raise specific and
    informative runtime errors.

    Our types are therefore less accurate for class-var access, but more accurate for
    instance-var access.
    """

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__("<stub>")

    def __getattr__(self, name: str) -> t.Any:
        if name == "user":
            _raise_attr_error("scopes")
        elif name == "resource_server":
            _raise_attr_error("resource_server")
        return super().__getattr__(name)

    def __getattribute__(self, name: str) -> t.Any:
        if name == "resource_server":
            _raise_attr_error("resource_server")
        return object.__getattribute__(self, name)


def _raise_attr_error(name: str) -> t.NoReturn:
    raise AttributeError(
        f"It is not valid to attempt to access the '{name}' attribute of the "
        "SpecificFlowClient class. "
        f"Instead, instantiate a SpecificFlowClient and access the '{name}' attribute "
        "from that instance."
    )


class SpecificFlowScopeBuilder(ScopeBuilder):
    """
    This defines the scopes for a single flow (as distinct from the Flows service).

    It primarily provides the `user` scope which is typically needed to start a run of
    a flow.

    Example usage:

    .. code-block:: python

        sb = SpecificFlowScopeBuilder("my-flow-id-here")
        flow_scope = sb.user
    """

    _CLASS_STUB = _SpecificFlowScopesClassStub()

    def __init__(self, flow_id: UUIDLike) -> None:
        self._flow_id = flow_id
        str_flow_id = str(flow_id)
        super().__init__(
            resource_server=str_flow_id,
            known_url_scopes=[("user", f"flow_{str_flow_id.replace('-', '_')}_user")],
        )
