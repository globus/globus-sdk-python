from __future__ import annotations

import typing as t

from globus_sdk import (
    AuthLoginClient,
    ConfidentialAppAuthClient,
    GlobusSDKUsageError,
    NativeAppAuthClient,
)
from globus_sdk._types import ScopeCollectionType, UUIDLike
from globus_sdk.experimental.auth_requirements_error import (
    GlobusAuthorizationParameters,
)
from globus_sdk.experimental.login_flow_manager import (
    CommandLineLoginFlowManager,
    LoginFlowManager,
)

from ._types import LoginFlowManagerProvider
from .app import GlobusApp
from .authorizer_factory import (
    AccessTokenAuthorizerFactory,
    RefreshTokenAuthorizerFactory,
)
from .config import DEFAULT_CONFIG, KNOWN_LOGIN_FLOW_MANAGERS, GlobusAppConfig


class UserApp(GlobusApp):
    """
    A ``GlobusApp`` for login methods that require an interactive flow with a user.

    ``UserApp``\\s are most commonly used with native application clients by passing a
    ``NativeAppAuthClient`` as ``login_client`` or the native application's
    ``client_id``.

    If using a templated client, either pass a ``ConfidentialAppAuthClient``
    as `login_client`` or the templated client's ``client_id`` and ``client_secret``.
    This will not work for standard confidential clients.

    By default a ``UserApp`` will create a ``CommandLineLoginFlowManager`` for
    running login flows, which can be overridden through ``config``.

    .. tab-set::

        .. tab-item:: Example Usage

            .. code-block:: python

                app = UserApp("myapp", client_id=NATIVE_APP_CLIENT_ID)
                client = TransferClient(app=app)
                res = client.endpoint_search("Tutorial Collection")

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

    def _initialize_authorizer_factory(self) -> None:
        if self.config.request_refresh_tokens:
            self._authorizer_factory = RefreshTokenAuthorizerFactory(
                token_storage=self.token_storage, auth_login_client=self._login_client
            )
        else:
            self._authorizer_factory = AccessTokenAuthorizerFactory(
                token_storage=self.token_storage
            )

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
