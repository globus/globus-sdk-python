from __future__ import annotations

import typing as t
import uuid

import globus_sdk
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.scopes import GCSCollectionScopes


# NOTE: this stub class idea is inspired by the SpecificFlowScopes class stub
# it implements the same interface as the base class, so it's type-compatible
# but it raises errors at runtime -- because it can't *actually* be populated with data
class _GCSCollectionScopesClassStub(GCSCollectionScopes):
    """
    This internal stub object ensures that the type deductions for type checkers (e.g.
    mypy) on SpecificFlowClient.scopes are correct.

    Primarily, it should be possible to access the `scopes` attribute, the `user`
    scope, and the `resource_server`, but these usages should raise specific and
    informative runtime errors.

    Our types are therefore less accurate for class-var access, but more accurate for
    instance-var access.
    """

    def __init__(self) -> None:
        super().__init__("<stub>")

    def __getattribute__(self, name: str) -> t.Any:
        if name == "https":
            _raise_attr_error("https")
        if name == "data_access":
            _raise_attr_error("data_access")
        if name == "resource_server":
            _raise_attr_error("resource_server")
        return object.__getattribute__(self, name)


class GCSCollectionClient(globus_sdk.BaseClient):
    """
    A client for interacting directly with a GCS Collection.
    Typically for HTTPS upload/download via HTTPS-enabled collections.

    .. note::

        Because the client communicates directly with paths on the collection, rather
        than with the Endpoint hosting it, the ``base_url`` parameter is required.

    .. sdk-sphinx-copy-params:: BaseClient

        :param collection_id: The ID of the collection.
    """

    scopes: GCSCollectionScopes = _GCSCollectionScopesClassStub()

    def __init__(
        self,
        collection_id: str | uuid.UUID,
        base_url: str,
        *,
        environment: str | None = None,
        app: globus_sdk.GlobusApp | None = None,
        app_scopes: list[globus_sdk.scopes.Scope] | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport: globus_sdk.transport.RequestsTransport | None = None,
        retry_config: globus_sdk.transport.RetryConfig | None = None,
    ) -> None:
        self.collection_id = str(collection_id)
        self.scopes = GCSCollectionScopes(self.collection_id)

        super().__init__(
            environment=environment,
            base_url=base_url,
            app=app,
            app_scopes=app_scopes,
            authorizer=authorizer,
            app_name=app_name,
            transport=transport,
            retry_config=retry_config,
        )

    @property
    def default_scope_requirements(self) -> list[globus_sdk.Scope]:
        return [self.scopes.https]


def _raise_attr_error(name: str) -> t.NoReturn:
    raise AttributeError(
        f"It is not valid to attempt to access the '{name}' attribute of the "
        "GCSCollectionClient class. "
        f"Instead, instantiate a GCSCollectionClient and access the '{name}' attribute "
        "from that instance."
    )
