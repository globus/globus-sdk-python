from __future__ import annotations

import abc
import os
import sys

from globus_sdk import (
    AuthClient,
    AuthLoginClient,
    ConfidentialAppAuthClient,
    NativeAppAuthClient,
    Scope,
)
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.experimental.auth_requirements_error import (
    GlobusAuthorizationParameters,
)
from globus_sdk.experimental.login_flow_manager import (
    CommandLineLoginFlowManager,
    LoginFlowManager,
)
from globus_sdk.experimental.tokenstorage import JSONTokenStorage, TokenStorage
from globus_sdk.scopes import AuthScopes

from ._validating_token_storage import ValidatingTokenStorage
from .authorizer_factory import (
    AccessTokenAuthorizerFactory,
    AuthorizerFactory,
    ClientCredentialsAuthorizerFactory,
    RefreshTokenAuthorizerFactory,
)


def _default_filename(app_name: str) -> str:
    r"""
    construct the filename for the default JSONTokenStorage to use

    on Windows, this is typically
        ~\AppData\Local\globus\{app_name}/tokens.json

    on Linux and macOS, we use
        ~/.globus/{app_name}/tokens.json
    """
    if sys.platform == "win32":
        # try to get the app data dir, preferring the local appdata
        datadir = os.getenv("LOCALAPPDATA", os.getenv("APPDATA"))
        if not datadir:
            home = os.path.expanduser("~")
            datadir = os.path.join(home, "AppData", "Local")
        return os.path.join(datadir, "globus", app_name, "tokens.json")
    else:
        return os.path.expanduser(f"~/.globus/{app_name}/tokens.json")


class GlobusAppConfig:
    """
    Various configuration options for controlling the behavior of a ``GlobusApp``.
    """

    def __init__(
        self,
        *,
        login_flow_manager: LoginFlowManager | None = None,
        token_storage: TokenStorage | None = None,
        refresh_tokens: bool = False,
    ):
        """
        :param login_flow_manager: a ``LoginFlowManager`` that will be used when
            driving login flows with a ``UserApp``. If not passed a
            ``CommandLineLoginFLowManager`` will be used. A ``ClientApp`` will
            error if this value is not None.
        :param token_storage: a ``TokenStorage`` instance or class that will
            be used for storing token data. If not passed a ``JSONTokenStorage``
            will be used.
        :param refresh_tokens: If True, the ``GlobusApp`` will request refresh tokens
            for long lived access.
        """
        self.refresh_tokens = refresh_tokens
        self.login_flow_manager = login_flow_manager
        self.token_storage = token_storage


class GlobusApp(metaclass=abc.ABCMeta):
    """
    ``GlobusApp` is an abstract base class providing an interface for simplifying
    authentication with Globus services.

    A ``GlobusApp`` manages scope requirements across multiple resource servers,
    runs login flows through its ``LoginFlowManager``, handles token storage and
    validation through its ``ValidatingTokenStorage``, and provides up-to-date
    authorizers from its ``AuthorizerFactory`` through ``get_authorizer``.

    In the near future, a ``GlobusApp`` will be accepted as an initialization parameter
    to any Globus service client, automatically handling the client's default
    scope requirements and providing the client an authorizer.
    """

    _login_client: AuthLoginClient
    _authorizer_factory: AuthorizerFactory[GlobusAuthorizer]

    def __init__(
        self,
        app_name: str,
        *,
        scope_requirements: dict[str, list[Scope]] | None = None,
        config: GlobusAppConfig | None = None,
    ):
        """
        :param app_name: A string to identify this app. Used for default tokenstorage
            location and in the future will be used to set user-agent when this app is
            attached to a service client
        :param scope_requirements: A dict of lists of required scopes indexed by
            their resource server.
        :config: A ``GlobusAppConfig`` used to control various behaviors of this app.
        """
        self.app_name = app_name

        if config:
            self.config = config
        else:
            # default config
            self.config = GlobusAppConfig()

        self._initialize_login_client()

        # get our initial scope requirements make sure we at least have "openid"
        # to get identity information for token validation
        auth_rs = str(AuthClient.resource_server)
        openid_scope = Scope(AuthScopes.openid)
        if scope_requirements:
            if auth_rs not in scope_requirements:
                scope_requirements[auth_rs] = [openid_scope]
            else:
                scope_requirements[auth_rs] = Scope.merge_scopes(
                    scope_requirements[auth_rs], [openid_scope]
                )
            self._scope_requirements = scope_requirements
        else:
            self._scope_requirements = {auth_rs: [openid_scope]}

        # either get config's TokenStorage, or make the default JSONTokenStorage
        if self.config.token_storage:
            self._token_storage = self.config.token_storage
        else:
            self._token_storage = JSONTokenStorage(
                filename=_default_filename(self.app_name)
            )

        # construct ValidatingTokenStorage around the TokenStorage and
        # our initial scope requirements
        self._validating_token_storage = ValidatingTokenStorage(
            token_storage=self._token_storage,
            scope_requirements=self._scope_requirements,
        )

        # initialize our authorizer factory
        self._initialize_authorizer_factory()

    @abc.abstractmethod
    def _initialize_login_client(self) -> None:
        """
        Initializes self._login_client to be used for making authorization requests.
        """

    @abc.abstractmethod
    def _initialize_authorizer_factory(self) -> None:
        """
        Initializes self._authorizer_factory to be used for generating authorizers to
        authorize requests.
        """

    @abc.abstractmethod
    def run_login_flow(
        self, auth_params: GlobusAuthorizationParameters | None = None
    ) -> None:
        """
        Run an authorization flow to get new tokens which are stored and available
        for the next authorizer gotten by get_authorizer.

        :param auth_params: A GlobusAuthorizationParameters to control how the user
            will authenticate. If not passed
        """

    def _auth_params_with_required_scopes(
        self,
        auth_params: GlobusAuthorizationParameters | None = None,
    ) -> GlobusAuthorizationParameters:
        """
        Either make a new GlobusAuthorizationParameters with this app's required scopes
        or combine this app's required scopes with given auth_params.
        """
        required_scopes = []
        for scope_list in self._scope_requirements.values():
            required_scopes.extend(scope_list)

        if auth_params:
            if auth_params.required_scopes:
                combined_scopes = Scope.merge_scopes(
                    required_scopes, [Scope(s) for s in auth_params.required_scopes]
                )
                auth_params.required_scopes = [str(s) for s in combined_scopes]
            else:
                auth_params.required_scopes = [str(s) for s in required_scopes]
            return auth_params

        else:
            return GlobusAuthorizationParameters(
                required_scopes=[str(s) for s in required_scopes]
            )

    def get_authorizer(self, resource_server: str) -> GlobusAuthorizer:
        """
        Get a ``GlobusAuthorizer`` from the app's authorizer factory for a specified
        resource server. The type of authorizer is dependent on the app.

        :param resource_server: the resource server the Authorizer will provide
            authorization headers for
        """
        return self._authorizer_factory.get_authorizer(resource_server)

    def add_scope_requirements(
        self, scope_requirements: dict[str, list[Scope]]
    ) -> None:
        """
        Add given scope requirements to the app's scope requirements.

        :param scope_requirements: a dict of Scopes indexed by resource server
            that will be added to this app's scope requirements
        """
        for resource_server, scopes in scope_requirements.items():
            if resource_server not in self._scope_requirements:
                self._scope_requirements[resource_server] = scopes

            else:
                self._scope_requirements[resource_server] = Scope.merge_scopes(
                    self._scope_requirements[resource_server], scopes
                )

        # update the app's ValidatingTokenStorage's scope requirements to enforce the
        # updated scope requirements
        self._validating_token_storage.scope_requirements = self._scope_requirements


class UserApp(GlobusApp):
    """
    A ``GlobusApp`` for login methods that require an interactive flow with a user.

    Can either use a native application client by only giving ``client_id`` or a
    templated client by giving both ``client_id`` and ``client_secret``.

    .. tab-set::

        .. tab-item:: Future Example Usage

            .. code-block:: python

                app = UserApp("myapp", client_id=NATIVE_APP_CLIENT_ID)
                client = TransferClient(app=app)
                res = client.operation_ls(COLLECTION_ID)

    """

    _login_client: NativeAppAuthClient | ConfidentialAppAuthClient
    _authorizer_factory: (  # type:ignore
        AccessTokenAuthorizerFactory | RefreshTokenAuthorizerFactory
    )

    def __init__(
        self,
        app_name: str,
        *,
        scope_requirements: dict[str, list[Scope]] | None = None,
        client_id: UUIDLike | None = None,
        client_secret: str | None = None,
        config: GlobusAppConfig | None = None,
    ):
        """
        :param app_name: A string to identify this app. Used for default tokenstorage
            location and in the future will be used to set user-agent when this app is
            attached to a service client
        :param scope_requirements: A dict of lists of required scopes indexed by
            their resource server.
        :param client_id: A UUID for the Globus client this app will use. This value
            is currently required in all cases.
        :param client_secret: If using a templated client, the value of its client
            secret. If omitted or passed as None the app is assumed to be a native
            app.
        :config: A ``GlobusAppConfig`` used to control various behaviors of this app.
        """

        # in the future we might use an environment variable if this is passed as None,
        # but for now client_id is required
        if client_id is None:
            raise ValueError("client_id is required")

        self.client_id = client_id
        self.client_secret = client_secret
        super().__init__(app_name, scope_requirements=scope_requirements, config=config)

        # either get config's LoginFlowManager
        # or make a default CommandLineLoginFlowManager
        if self.config.login_flow_manager:
            self._login_flow_manager = self.config.login_flow_manager
        else:
            self._login_flow_manager = CommandLineLoginFlowManager(
                self._login_client,
                refresh_tokens=self.config.refresh_tokens,
            )

    def _initialize_login_client(self) -> None:
        if self.client_secret:
            self._login_client = ConfidentialAppAuthClient(
                app_name=self.app_name,
                client_id=self.client_id,
                client_secret=self.client_secret,
            )
        else:
            self._login_client = NativeAppAuthClient(
                app_name=self.app_name,
                client_id=self.client_id,
            )

    def _initialize_authorizer_factory(self) -> None:
        if self.config.refresh_tokens:
            self._authorizer_factory = RefreshTokenAuthorizerFactory(
                token_storage=self._validating_token_storage,
                auth_login_client=self._login_client,
            )
        else:
            self._authorizer_factory = AccessTokenAuthorizerFactory(
                token_storage=self._validating_token_storage,
            )

    def run_login_flow(
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


class ClientApp(GlobusApp):
    """
    A ``GlobusApp`` using client credentials - useful for service accounts and
    automation use cases.

    .. tab-set::

        .. tab-item:: Future Example Usage

            .. code-block:: python

                app = UserApp("myapp", CLIENT_ID, CLIENT_SECRET)
                client = TransferClient(app=app)
                res = client.operation_ls(COLLECTION_ID)

    """

    _login_client: ConfidentialAppAuthClient
    _authorizer_factory: ClientCredentialsAuthorizerFactory  # type:ignore

    def __init__(
        self,
        app_name: str,
        client_id: UUIDLike,
        client_secret: str,
        *,
        scope_requirements: dict[str, list[Scope]] | None = None,
        config: GlobusAppConfig | None = None,
    ):
        """
        :param app_name: A string to identify this app. Used for default tokenstorage
            location and in the future will be used to set user-agent when this app is
            attached to a service client
        :param scope_requirements: A dict of lists of required scopes indexed by
            their resource server.
        :param client_id: A UUID for the Globus client this app will use. This value
            is currently required in all cases.
        :param client_secret: The client secret for the
        :config: A ``GlobusAppConfig`` used to control various behaviors of this app.
        """
        if config and config.login_flow_manager is not None:
            raise ValueError("a ClientApp cannot use a login_flow_manager")

        self.client_id = client_id
        self.client_secret = client_secret
        super().__init__(app_name, scope_requirements=scope_requirements, config=config)

    def _initialize_login_client(self) -> None:
        self._login_client = ConfidentialAppAuthClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            app_name=self.app_name,
        )

    def _initialize_authorizer_factory(self) -> None:
        self._authorizer_factory = ClientCredentialsAuthorizerFactory(
            token_storage=self._validating_token_storage,
            confidential_client=self._login_client,
        )

    def run_login_flow(
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
