from __future__ import annotations

import abc
import dataclasses
import sys
import typing as t
from dataclasses import dataclass

from globus_sdk import (
    AuthClient,
    AuthLoginClient,
    ConfidentialAppAuthClient,
    NativeAppAuthClient,
    Scope,
)
from globus_sdk import config as sdk_config
from globus_sdk._types import ScopeCollectionType, UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.exc import GlobusSDKUsageError
from globus_sdk.experimental.auth_requirements_error import (
    GlobusAuthorizationParameters,
)
from globus_sdk.experimental.login_flow_manager import (
    CommandLineLoginFlowManager,
    LocalServerLoginFlowManager,
    LoginFlowManager,
)
from globus_sdk.experimental.tokenstorage import (
    JSONTokenStorage,
    MemoryTokenStorage,
    SQLiteTokenStorage,
    TokenStorage,
)
from globus_sdk.scopes import AuthScopes, scopes_to_scope_list

from ._validating_token_storage import ValidatingTokenStorage
from .authorizer_factory import (
    AccessTokenAuthorizerFactory,
    AuthorizerFactory,
    ClientCredentialsAuthorizerFactory,
    RefreshTokenAuthorizerFactory,
)
from .errors import IdentityMismatchError, TokenValidationError

if sys.version_info < (3, 8):
    from typing_extensions import Protocol, runtime_checkable
else:
    from typing import Protocol, runtime_checkable


@runtime_checkable
class TokenStorageProvider(Protocol):
    @classmethod
    def for_globus_app(
        cls, client_id: UUIDLike, app_name: str, config: GlobusAppConfig, namespace: str
    ) -> TokenStorage: ...


@runtime_checkable
class LoginFlowManagerProvider(Protocol):
    @classmethod
    def for_globus_app(
        cls, app_name: str, login_client: AuthLoginClient, config: GlobusAppConfig
    ) -> LoginFlowManager: ...


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


KnownLoginFlowManager = t.Literal["command-line", "local-server"]
KNOWN_LOGIN_FLOW_MANAGERS: dict[KnownLoginFlowManager, LoginFlowManagerProvider] = {
    "command-line": CommandLineLoginFlowManager,
    "local-server": LocalServerLoginFlowManager,
}

KnownTokenStorage = t.Literal["json", "sqlite", "memory"]
KNOWN_TOKEN_STORAGES: dict[KnownTokenStorage, t.Type[TokenStorageProvider]] = {
    "json": JSONTokenStorage,
    "sqlite": SQLiteTokenStorage,
    "memory": MemoryTokenStorage,
}


@dataclass(frozen=True)
class GlobusAppConfig:
    """
    Various configuration options for controlling the behavior of a ``GlobusApp``.

    :param login_flow_manager: An optional ``LoginFlowManager`` instance, provider,
        or identifier ("command-line" or "local-server").
        For a ``UserApp``, defaults to "command-line".
        For a ``ClientApp``, this value is not supported.
    :param login_redirect_uri: The redirect URI to use for login flows.
        For a "local-server" login flow manager, this value is not supported.
        For a native client, this value defaults to a globus-hosted helper page.
        For a confidential client, this value is required.
    :param request_refresh_tokens: If True, the ``GlobusApp`` will request refresh
        tokens for long-lived access.
    :param token_storage: A ``TokenStorage`` instance, provider, or identifier
        ("json", "sqlite", or "memory").
        Default: "json"
    :param token_validation_error_handler: A callable that will be called when a
        token validation error is encountered. The default behavior is to retry the
        login flow automatically.
    :param environment: The Globus environment being targeted by this app. This is
        predominately for internal use and can be ignored in most cases.
    """

    login_flow_manager: (
        KnownLoginFlowManager | LoginFlowManagerProvider | LoginFlowManager | None
    ) = None
    login_redirect_uri: str | None = None
    token_storage: KnownTokenStorage | TokenStorageProvider | TokenStorage = "json"
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
    ``GlobusApp`` is an abstract base class providing an interface for simplifying
    authentication with Globus services.

    A ``GlobusApp`` manages scope requirements across multiple resource servers,
    runs login flows through its ``LoginFlowManager``, handles token storage and
    validation through its ``ValidatingTokenStorage``, and provides up-to-date
    authorizers from its ``AuthorizerFactory`` through ``get_authorizer``.

    A ``GlobusApp`` is accepted as an initialization parameter to any SDK-provided
    service client, automatically handling the client's default scope requirements and
    providing the client with an authorizer.
    """

    _login_client: AuthLoginClient
    _authorizer_factory: AuthorizerFactory[GlobusAuthorizer]

    def __init__(
        self,
        app_name: str = "Unnamed Globus App",
        *,
        login_client: AuthLoginClient | None = None,
        client_id: UUIDLike | None = None,
        client_secret: str | None = None,
        scope_requirements: dict[str, ScopeCollectionType] | None = None,
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
        :param scope_requirements: A dictionary of scope requirements indexed by
            resource server. The dict value may be a scope, scope string, or list of
            scopes or scope strings.
        :config: A ``GlobusAppConfig`` used to control various behaviors of this app.
        """
        self.app_name = app_name
        self.config = config

        self.client_id, self._login_client = self._resolve_client_info(
            app_name=self.app_name,
            config=self.config,
            client_id=client_id,
            client_secret=client_secret,
            login_client=login_client,
        )
        self._scope_requirements = self._resolve_scope_requirements(scope_requirements)
        self._token_storage = self._resolve_token_storage(
            app_name=self.app_name,
            client_id=self.client_id,
            config=self.config,
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

    def _resolve_scope_requirements(
        self, scope_requirements: dict[str, ScopeCollectionType] | None
    ) -> dict[str, list[Scope]]:
        if scope_requirements is None:
            return {}

        return {
            resource_server: scopes_to_scope_list(scopes)
            for resource_server, scopes in scope_requirements.items()
        }

    def _resolve_client_info(
        self,
        app_name: str,
        config: GlobusAppConfig,
        login_client: AuthLoginClient | None,
        client_id: UUIDLike | None,
        client_secret: str | None,
    ) -> tuple[UUIDLike, AuthLoginClient]:
        """
        Extracts a client_id and login_client from GlobusApp initialization parameters,
        validating that the parameters were provided correctly.

        Depending on which parameters were provided, this method will either:
            1.  Create a new login client from the supplied credentials.
                *   The actual initialization is performed by the subclass using the
                    abstract method: _initialize_login_client``.
            2.  Extract the client_id from a supplied login_client.

        :returns: tuple of client_id and login_client
        :raises: GlobusSDKUsageError if a single client ID or login client could not be
            definitively resolved.
        """
        if login_client and client_id:
            msg = "Mutually exclusive parameters: client_id and login_client."
            raise GlobusSDKUsageError(msg)

        if login_client:
            # User provided an explicit login client, extract the client_id.
            if login_client.client_id is None:
                msg = "A GlobusApp login_client must have a discoverable client_id."
                raise GlobusSDKUsageError(msg)
            if login_client.environment != config.environment:
                raise GlobusSDKUsageError(
                    "[Environment Mismatch] The login_client's environment "
                    f"({login_client.environment}) does not match the GlobusApp's "
                    f"configured environment ({config.environment})."
                )

            return login_client.client_id, login_client

        elif client_id:
            # User provided an explicit client_id, construct a login client
            login_client = self._initialize_login_client(
                app_name, config, client_id, client_secret
            )
            return client_id, login_client

        else:
            raise GlobusSDKUsageError(
                "Could not set up a globus login client. One of client_id or "
                "login_client is required."
            )

    @abc.abstractmethod
    def _initialize_login_client(
        self,
        app_name: str,
        config: GlobusAppConfig,
        client_id: UUIDLike,
        client_secret: str | None,
    ) -> AuthLoginClient:
        """
        Initializes and returns an AuthLoginClient to be used in authorization requests.
        """

    def _resolve_token_storage(
        self, app_name: str, client_id: UUIDLike, config: GlobusAppConfig
    ) -> TokenStorage:
        """
        Resolve the raw token storage to be used by the app.

        This may be:
            1.  A TokenStorage instance provided by the user, which we use directly.
            2.  A TokenStorageProvider, which we use to get a TokenStorage.
            3.  A string value, which we map onto supported TokenStorage types.

        :returns: TokenStorage instance to be used by the app.
        :raises: GlobusSDKUsageError if the provided token_storage value is unsupported.
        """
        token_storage = config.token_storage
        # TODO - make namespace configurable
        namespace = "DEFAULT"
        if isinstance(token_storage, TokenStorage):
            return token_storage

        elif isinstance(token_storage, TokenStorageProvider):
            return token_storage.for_globus_app(client_id, app_name, config, namespace)

        elif token_storage in KNOWN_TOKEN_STORAGES:
            provider = KNOWN_TOKEN_STORAGES[token_storage]
            return provider.for_globus_app(client_id, app_name, config, namespace)

        raise GlobusSDKUsageError(
            f"Unsupported token_storage value: {token_storage}. Must be a "
            f"TokenStorage, TokenStorageProvider, or a supported string value."
        )

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
        self, scope_requirements: dict[str, ScopeCollectionType]
    ) -> None:
        """
        Add given scope requirements to the app's scope requirements. Any duplicate
        requirements will be deduplicated later at authorization url creation time.

        :param scope_requirements: a dict of Scopes indexed by resource server
            that will be added to this app's scope requirements
        """
        for resource_server, scopes in scope_requirements.items():
            curr = self._scope_requirements.setdefault(resource_server, [])
            curr.extend(scopes_to_scope_list(scopes))

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
        scope_requirements: dict[str, ScopeCollectionType] | None = None,
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

        return provider.for_globus_app(app_name, login_client, config)

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

    ``ClientApp``\\s are always used with confidential clients either by passing
    a ``ConfidentialAppAuthClient`` as ``login_client`` or providing the client's
    ``client_id`` and ``client_secret`` pair.

    ``ClientApp``\\s do not use a ``LoginFlowManager`` and will raise an error
    if given one through ``config``.

    .. tab-set::

        .. tab-item:: Example Usage

            .. code-block:: python

                app = ClientApp("myapp", CLIENT_ID, CLIENT_SECRET)
                client = TransferClient(app=app)
                res = client.endpoint_search("Tutorial Collection")

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
        config: GlobusAppConfig = _DEFAULT_CONFIG,
    ):
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
