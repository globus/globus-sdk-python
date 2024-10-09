from __future__ import annotations

from globus_sdk import AuthLoginClient, ConfidentialAppAuthClient, GlobusSDKUsageError
from globus_sdk._types import ScopeCollectionType, UUIDLike
from globus_sdk.gare import GlobusAuthorizationParameters

from .app import GlobusApp
from .authorizer_factory import ClientCredentialsAuthorizerFactory
from .config import DEFAULT_CONFIG, GlobusAppConfig


class ClientApp(GlobusApp):
    """
    A ``GlobusApp`` for managing authentication state of a service account for use
    in service clients.

    A ``ClientApp`` requires the use of a confidential client created in a
    `Globus Project <https://app.globus.org/settings/developers>`. Client info may
    be passed either with the **client_id** and **client_secret** parameters or as
    a full **login_client**.

    ``ClientApps`` are configured by supplying a :class:`GlobusAppConfig` object to the
    **config** parameter. Of note however, **login_flow_manager** must not be set; a
    ``ClientApp`` does not use a login flow manager.

    See :class:`GlobusApp` for method signatures.

    .. rubric:: Example Usage:

    .. code-block:: python

        app = ClientApp("myapp", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        transfer_client = TransferClient(app=app)
        res = transfer_client.endpoint_search("Tutorial Collection")


    :param app_name: A human-readable string to identify this app.
    :param login_client: A login client bound to a specific native client id or
        confidential client id/secret. Mutually exclusive with **client_id** and
        **client_secret**.
    :param client_id: A confidential client ID. Mutually exclusive with
        **login_client**.
    :param client_secret: A confidential client secret. Mutually exclusive with
        **login_client**.
    :param scope_requirements: A mapping of resource server to initial scope
        requirements.
    :param config: A data class containing configuration parameters for the app.
    """

    _login_client: ConfidentialAppAuthClient
    _authorizer_factory: ClientCredentialsAuthorizerFactory  # type:ignore

    def __init__(
        self,
        app_name: str = "Unnamed Globus App",
        *,
        login_client: ConfidentialAppAuthClient | None = None,
        client_id: UUIDLike | None = None,
        client_secret: str | None = None,
        scope_requirements: dict[str, ScopeCollectionType] | None = None,
        config: GlobusAppConfig = DEFAULT_CONFIG,
    ) -> None:
        if config.login_flow_manager is not None:
            raise GlobusSDKUsageError("A ClientApp cannot use a login_flow_manager")

        if login_client and not isinstance(login_client, ConfidentialAppAuthClient):
            raise GlobusSDKUsageError(
                "A ClientApp must use a ConfidentialAppAuthClient for its login_client"
            )

        super().__init__(
            app_name,
            login_client=login_client,
            client_id=client_id,
            client_secret=client_secret,
            scope_requirements=scope_requirements,
            config=config,
        )

    def _initialize_login_client(
        self,
        app_name: str,
        config: GlobusAppConfig,
        client_id: UUIDLike,
        client_secret: str | None,
    ) -> AuthLoginClient:
        if not client_secret:
            raise GlobusSDKUsageError(
                "A ClientApp requires a client_secret to initialize its own login "
                "client."
            )

        return ConfidentialAppAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            app_name=app_name,
            environment=config.environment,
        )

    def _initialize_authorizer_factory(self) -> None:
        self._authorizer_factory = ClientCredentialsAuthorizerFactory(
            token_storage=self.token_storage,
            confidential_client=self._login_client,
            scope_requirements=self._scope_requirements,
        )

    def _run_login_flow(
        self, auth_params: GlobusAuthorizationParameters | None = None
    ) -> None:
        """
        Run an authorization flow to get new tokens which are stored and available
        for the next authorizer gotten by get_authorizer.

        As a ClientApp this is just a client credentials call.

        :param auth_params: A GlobusAuthorizationParameters to control authentication
            only the required_scopes parameter is used.
        """
        auth_params = self._auth_params_with_required_scopes(auth_params)
        token_response = self._login_client.oauth2_client_credentials_tokens(
            requested_scopes=auth_params.required_scopes
        )
        self._authorizer_factory.store_token_response_and_clear_cache(token_response)
