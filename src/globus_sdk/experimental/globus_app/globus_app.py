from __future__ import annotations

import abc
import dataclasses
import os
import sys
from dataclasses import dataclass

from globus_sdk import (
    AuthClient,
    AuthLoginClient,
    ConfidentialAppAuthClient,
    NativeAppAuthClient,
    Scope,
)
from globus_sdk import config as sdk_config
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.exc import GlobusSDKUsageError
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
from .errors import IdentityMismatchError, TokenValidationError

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol


def _default_filename(app_name: str, environment: str) -> str:
    r"""
    construct the filename for the default JSONTokenStorage to use

    on Windows, this is typically
        ~\AppData\Local\globus\app\{app_name}/tokens.json

    on Linux and macOS, we use
        ~/.globus/app/{app_name}/tokens.json
    """
    environment_prefix = f"{environment}-"
    if environment == "production":
        environment_prefix = ""
    filename = f"{environment_prefix}tokens.json"

    if sys.platform == "win32":
        # try to get the app data dir, preferring the local appdata
        datadir = os.getenv("LOCALAPPDATA", os.getenv("APPDATA"))
        if not datadir:
            home = os.path.expanduser("~")
            datadir = os.path.join(home, "AppData", "Local")
        return os.path.join(datadir, "globus", "app", app_name, filename)
    else:
        return os.path.expanduser(f"~/.globus/app/{app_name}/{filename}")


class TokenValidationErrorHandler(Protocol):
    def __call__(self, app: GlobusApp, error: TokenValidationError) -> None: ...


def resolve_by_login_flow(app: GlobusApp, error: TokenValidationError) -> None:
    """
    An error handler for GlobusApp token access errors that will retry the
    login flow if the error is a TokenValidationError.

    :param app: The GlobusApp instance which encountered an error.
    :param error: The encountered token validation error.
    """
    if isinstance(error, IdentityMismatchError):
        # An identity mismatch error indicates incorrect use of the app. Not something
        #   that can be resolved by running a login flow.
        raise error

    app.run_login_flow()


@dataclass(frozen=True)
class GlobusAppConfig:
    """
    Various configuration options for controlling the behavior of a ``GlobusApp``.

    :param login_flow_manager: an optional ``LoginFlowManager`` instance or class.
        An instance will be used directly when driving app login flows. A class will
        be initialized with the app's ``login_client`` and this config's
        ``request_refresh_tokens``.
        If not given the default behavior will depend on the type of ``GlobusApp``.
    :param token_storage: a ``TokenStorage`` instance or class that will
        be used for storing token data. If not passed a ``JSONTokenStorage``
        will be used.
    :param request_refresh_tokens: If True, the ``GlobusApp`` will request refresh
        tokens for long-lived access.
    :param token_validation_error_handler: A callable that will be called when a
        token validation error is encountered. The default behavior is to retry the
        login flow automatically.
    :param environment: The Globus environment being targeted by this app. This is
        predominately for internal use and can be ignored in most cases.
    """

    login_flow_manager: LoginFlowManager | type[LoginFlowManager] | None = None
    token_storage: TokenStorage | None = None
    request_refresh_tokens: bool = False
    token_validation_error_handler: TokenValidationErrorHandler | None = (
        resolve_by_login_flow
    )
    environment: str = dataclasses.field(
        default_factory=sdk_config.get_environment_name
    )


_DEFAULT_CONFIG = GlobusAppConfig()


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
        login_client: AuthLoginClient | None = None,
        client_id: UUIDLike | None = None,
        client_secret: str | None = None,
        scope_requirements: dict[str, list[Scope]] | None = None,
        config: GlobusAppConfig = _DEFAULT_CONFIG,
    ):
        """
        :param app_name: A string to identify this app. Used for default tokenstorage
            location and in the future will be used to set user-agent when this app is
            attached to a service client
        :param login_client: An ``AuthLoginCLient`` that will be used for running
            authentication flows. Different classes of ``GlobusApp`` may require
            specific classes of ``AuthLoginClient``. ``Mutually exclusive with
            ``client_id`` and ``client_secret``.
        :client_id: A client UUID used to construct an ``AuthLoginCLient`` for running
            authentication flows. The type of ``AuthLoginCLient`` will depend on the
            type of ``GlobusApp``. Mutually exclusive with ``login_client``.
        :client_secret: The value of the client secret for ``client_id`` if it uses
            secrets. Mutually exclusive with ``login_client``.
        :param scope_requirements: A dict of lists of required scopes indexed by
            their resource server.
        :config: A ``GlobusAppConfig`` used to control various behaviors of this app.
        """
        self.app_name = app_name
        self.config = config

        if login_client:
            if client_id or client_secret:
                raise GlobusSDKUsageError(
                    "login_client is mutually exclusive with client_id and "
                    "client_secret."
                )
            if login_client.environment != self.config.environment:
                raise GlobusSDKUsageError(
                    f"[Environment Mismatch] The login_client's environment "
                    f"({login_client.environment}) does not match the GlobusApp's "
                    f"configured environment ({self.config.environment})."
                )

        self.client_id: UUIDLike | None
        if login_client:
            self._login_client = login_client
            self.client_id = login_client.client_id
        else:
            self.client_id = client_id
            self._initialize_login_client(client_secret)

        self._scope_requirements = scope_requirements or {}

        # either get config's TokenStorage, or make the default JSONTokenStorage
        if self.config.token_storage:
            self._token_storage = self.config.token_storage
        else:
            self._token_storage = JSONTokenStorage(
                filename=_default_filename(self.app_name, self.config.environment)
            )

        # construct ValidatingTokenStorage around the TokenStorage and
        # our initial scope requirements
        self._validating_token_storage = ValidatingTokenStorage(
            token_storage=self._token_storage,
            scope_requirements=self._scope_requirements,
        )

        # initialize our authorizer factory
        self._initialize_authorizer_factory()

        # create a consent client for token validation
        # reducing the scope requirements to barebones openid (user identification)
        # additionally, this will ensure that openid scope requirement is always
        # registered (it's required for token identity validation).
        consent_client = AuthClient(app=self, app_scopes=[Scope(AuthScopes.openid)])
        self._validating_token_storage.set_consent_client(consent_client)

    @abc.abstractmethod
    def _initialize_login_client(self, client_secret: str | None) -> None:
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

        if not auth_params:
            auth_params = GlobusAuthorizationParameters()

        # merge scopes for deduplication to minimize url request length
        # this is useful even if there weren't any auth_param scope requirements
        # as the app's scope_requirements can have duplicates
        combined_scopes = Scope.merge_scopes(
            required_scopes, [Scope(s) for s in auth_params.required_scopes or []]
        )
        auth_params.required_scopes = [str(s) for s in combined_scopes]

        return auth_params

    def get_authorizer(self, resource_server: str) -> GlobusAuthorizer:
        """
        Get a ``GlobusAuthorizer`` from the app's authorizer factory for a specified
        resource server. The type of authorizer is dependent on the app.

        :param resource_server: the resource server the Authorizer will provide
            authorization headers for
        """
        try:
            return self._authorizer_factory.get_authorizer(resource_server)
        except TokenValidationError as e:
            if self.config.token_validation_error_handler:
                # Dispatch to the configured error handler if one is set then retry.
                self.config.token_validation_error_handler(self, e)
                return self._authorizer_factory.get_authorizer(resource_server)
            raise e

    def add_scope_requirements(
        self, scope_requirements: dict[str, list[Scope]]
    ) -> None:
        """
        Add given scope requirements to the app's scope requirements. Any duplicate
        requirements will be deduplicated later at authorization url creation time.

        :param scope_requirements: a dict of Scopes indexed by resource server
            that will be added to this app's scope requirements
        """
        for resource_server, scopes in scope_requirements.items():
            if resource_server not in self._scope_requirements:
                self._scope_requirements[resource_server] = scopes[:]
            else:
                self._scope_requirements[resource_server].extend(scopes)

        self._authorizer_factory.clear_cache(*scope_requirements.keys())

    def get_scope_requirements(self, resource_server: str) -> tuple[Scope, ...]:
        """
        Get an immutable copy of the collection scope requirements currently defined
        on a resource server.

        :param resource_server: the resource server to get scope requirements for
        """
        return tuple(self._scope_requirements.get(resource_server, []))


class UserApp(GlobusApp):
    """
    A ``GlobusApp`` for login methods that require an interactive flow with a user.

    ``UserApp`s are most commonly used with native application clients by passing a
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
                app.run_login_flow()
                res = client.endpoint_search("Tutorial Collection")

    """

    _login_client: NativeAppAuthClient | ConfidentialAppAuthClient
    _authorizer_factory: (  # type:ignore
        AccessTokenAuthorizerFactory | RefreshTokenAuthorizerFactory
    )

    def __init__(
        self,
        app_name: str,
        *,
        login_client: AuthLoginClient | None = None,
        client_id: UUIDLike | None = None,
        client_secret: str | None = None,
        scope_requirements: dict[str, list[Scope]] | None = None,
        config: GlobusAppConfig = _DEFAULT_CONFIG,
    ):
        super().__init__(
            app_name,
            login_client=login_client,
            client_id=client_id,
            client_secret=client_secret,
            scope_requirements=scope_requirements,
            config=config,
        )

        # get or instantiate config's login_flow_manager
        if self.config.login_flow_manager:
            if isinstance(self.config.login_flow_manager, LoginFlowManager):
                self._login_flow_manager = self.config.login_flow_manager
            elif isinstance(self.config.login_flow_manager, type(LoginFlowManager)):
                self._login_flow_manager = self.config.login_flow_manager(
                    self._login_client,
                    request_refresh_tokens=self.config.request_refresh_tokens,
                )
            else:
                raise TypeError(
                    "login_flow_manager must be a LoginFlowManager instance or class"
                )
        # or make a default CommandLineLoginFlowManager
        else:
            self._login_flow_manager = CommandLineLoginFlowManager(
                self._login_client,
                request_refresh_tokens=self.config.request_refresh_tokens,
            )

    def _initialize_login_client(self, client_secret: str | None) -> None:
        if self.client_id is None:
            raise GlobusSDKUsageError(
                "One of either client_id or login_client is required."
            )

        if client_secret:
            self._login_client = ConfidentialAppAuthClient(
                app_name=self.app_name,
                client_id=self.client_id,
                client_secret=client_secret,
                environment=self.config.environment,
            )
        else:
            self._login_client = NativeAppAuthClient(
                app_name=self.app_name,
                client_id=self.client_id,
                environment=self.config.environment,
            )

    def _initialize_authorizer_factory(self) -> None:
        if self.config.request_refresh_tokens:
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

    ``ClientApp``s are always used with confidential clients either by passing
    a ``ConfidentialAppAuthClient`` as ``login_client`` or providing the client's
    ``client_id`` and ``client_secret`` pair.

    ``ClientApp``s do not use a ``LoginFlowManager`` and will raise an error
    if given one through ``config``.

    .. tab-set::

        .. tab-item:: Example Usage

            .. code-block:: python

                app = UserApp("myapp", CLIENT_ID, CLIENT_SECRET)
                client = TransferClient(app=app)
                app.run_login_flow()
                res = client.endpoint_search("Tutorial Collection")

    """

    _login_client: ConfidentialAppAuthClient
    _authorizer_factory: ClientCredentialsAuthorizerFactory  # type:ignore

    def __init__(
        self,
        app_name: str,
        *,
        login_client: ConfidentialAppAuthClient | None = None,
        client_id: UUIDLike | None = None,
        client_secret: str | None = None,
        scope_requirements: dict[str, list[Scope]] | None = None,
        config: GlobusAppConfig = _DEFAULT_CONFIG,
    ):
        if config and config.login_flow_manager is not None:
            raise ValueError("a ClientApp cannot use a login_flow_manager")

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

    def _initialize_login_client(self, client_secret: str | None) -> None:
        if not (self.client_id and client_secret):
            raise GlobusSDKUsageError(
                "Either login_client or both client_id and client_secret are required"
            )

        self._login_client = ConfidentialAppAuthClient(
            client_id=self.client_id,
            client_secret=client_secret,
            app_name=self.app_name,
            environment=self.config.environment,
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
