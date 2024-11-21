from __future__ import annotations

import typing as t

from globus_sdk import (
    AuthClient,
    AuthLoginClient,
    ConfidentialAppAuthClient,
    GlobusSDKUsageError,
    NativeAppAuthClient,
    Scope,
)
from globus_sdk._types import ScopeCollectionType, UUIDLike
from globus_sdk.gare import GlobusAuthorizationParameters
from globus_sdk.login_flows import CommandLineLoginFlowManager, LoginFlowManager
from globus_sdk.tokenstorage import (
    HasRefreshTokensValidator,
    NotExpiredValidator,
    TokenStorage,
    UnchangingIdentityIDValidator,
    ValidatingTokenStorage,
)

from .app import GlobusApp
from .authorizer_factory import (
    AccessTokenAuthorizerFactory,
    RefreshTokenAuthorizerFactory,
)
from .config import DEFAULT_CONFIG, KNOWN_LOGIN_FLOW_MANAGERS, GlobusAppConfig
from .protocols import LoginFlowManagerProvider


class UserApp(GlobusApp):
    """
    A ``GlobusApp`` for managing authentication state of a user for use in service
    clients.

    Typically, a ``UserApp`` will use a native client, requiring a **client_id**
    created in a `Globus Project <https://app.globus.org/settings/developers>`_.
    More advanced use cases however, may additionally supply a **client_secret** or
    full **login_client** with confidential client credentials.

    ``UserApps`` are configured by supplying a :class:`GlobusAppConfig` object to the
    **config** parameter. Of note, login flow behavior involves printing and prompting
    the user for input using std::in and std::out. This behavior can be customized with
    the **login_flow_manager** config attribute.

    See :class:`GlobusApp` for method signatures.

    .. rubric:: Example Usage:

    .. code-block:: python

        app = UserApp("myapp", client_id=NATIVE_CLIENT_ID)
        transfer_client = TransferClient(app=app)
        res = transfer_client.endpoint_search("Tutorial Collection")

    :param app_name: A human-readable string to identify this app.
    :param login_client: A login client bound to a specific native client id or
        confidential client id/secret. Mutually exclusive with **client_id** and
        **client_secret**.
    :param client_id: A native or confidential client ID. Mutually exclusive with
        **login_client**.
    :param client_secret: A confidential client secret. Mutually exclusive with
        **login_client**.
    :param scope_requirements: A mapping of resource server to initial scope
        requirements.
    :param config: A data class containing configuration parameters for the app.
    """

    _login_client: NativeAppAuthClient | ConfidentialAppAuthClient
    _authorizer_factory: (  # type:ignore
        AccessTokenAuthorizerFactory | RefreshTokenAuthorizerFactory
    )

    def __init__(
        self,
        app_name: str = "Unnamed Globus App",
        *,
        login_client: AuthLoginClient | None = None,
        client_id: UUIDLike | None = None,
        client_secret: str | None = None,
        scope_requirements: t.Mapping[str, ScopeCollectionType] | None = None,
        config: GlobusAppConfig = DEFAULT_CONFIG,
    ) -> None:
        super().__init__(
            app_name,
            login_client=login_client,
            client_id=client_id,
            client_secret=client_secret,
            scope_requirements=scope_requirements,
            config=config,
        )

        self._login_flow_manager = self._resolve_login_flow_manager(
            app_name=self.app_name,
            login_client=self._login_client,
            config=config,
        )

    def _resolve_login_flow_manager(
        self, app_name: str, login_client: AuthLoginClient, config: GlobusAppConfig
    ) -> LoginFlowManager:
        login_flow_manager = config.login_flow_manager
        if isinstance(login_flow_manager, LoginFlowManager):
            return login_flow_manager

        elif isinstance(login_flow_manager, LoginFlowManagerProvider):
            provider = login_flow_manager
        elif login_flow_manager is None:
            provider = CommandLineLoginFlowManager
        elif login_flow_manager in KNOWN_LOGIN_FLOW_MANAGERS:
            provider = KNOWN_LOGIN_FLOW_MANAGERS[login_flow_manager]
        else:
            allowed_keys = ", ".join(repr(k) for k in KNOWN_LOGIN_FLOW_MANAGERS.keys())
            raise GlobusSDKUsageError(
                f"Unsupported login_flow_manager value: {login_flow_manager!r}. "
                f"Expected {allowed_keys}, a <LoginFlowManagerProvider>, or a "
                f"<LoginFlowManager>."
            )

        return provider.for_globus_app(
            app_name=app_name, config=config, login_client=login_client
        )

    def _initialize_login_client(
        self,
        app_name: str,
        config: GlobusAppConfig,
        client_id: UUIDLike,
        client_secret: str | None,
    ) -> AuthLoginClient:
        if client_secret:
            return ConfidentialAppAuthClient(
                app_name=app_name,
                client_id=client_id,
                client_secret=client_secret,
                environment=config.environment,
            )
        else:
            return NativeAppAuthClient(
                app_name=app_name,
                client_id=client_id,
                environment=config.environment,
            )

    def _initialize_validating_token_storage(
        self,
        token_storage: TokenStorage,
        consent_client: AuthClient,
        scope_requirements: t.Mapping[str, t.Sequence[Scope]],
    ) -> ValidatingTokenStorage:
        validating_token_storage = super()._initialize_validating_token_storage(
            token_storage, consent_client, scope_requirements
        )
        validating_token_storage.validators.append(UnchangingIdentityIDValidator())
        return validating_token_storage

    def _initialize_authorizer_factory(self) -> None:
        if self.config.request_refresh_tokens:
            self._authorizer_factory = RefreshTokenAuthorizerFactory(
                token_storage=self.token_storage, auth_login_client=self._login_client
            )
            self.token_storage.validators.insert(0, HasRefreshTokensValidator())
        else:
            self._authorizer_factory = AccessTokenAuthorizerFactory(
                token_storage=self.token_storage
            )
            self.token_storage.validators.insert(0, NotExpiredValidator())

    def _run_login_flow(
        self, auth_params: GlobusAuthorizationParameters | None = None
    ) -> None:
        """
        Run an authorization flow to get new tokens which are stored and available
        for the next authorizer gotten by get_authorizer.

        As a UserApp this always involves an interactive login flow with the user
        driven by the app's LoginFlowManager.

        :param auth_params: A GlobusAuthorizationParameters to control how the user
            will authenticate. If not passed
        """
        auth_params = self._auth_params_with_required_scopes(auth_params)
        token_response = self._login_flow_manager.run_login_flow(auth_params)
        self._authorizer_factory.store_token_response_and_clear_cache(token_response)
