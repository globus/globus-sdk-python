from __future__ import annotations

import abc
import contextlib
import copy
import typing as t

from globus_sdk import (
    AuthClient,
    AuthLoginClient,
    GlobusSDKUsageError,
    IDTokenDecoder,
    Scope,
)
from globus_sdk._types import ScopeCollectionType, UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.gare import GlobusAuthorizationParameters
from globus_sdk.scopes import AuthScopes, scopes_to_scope_list
from globus_sdk.tokenstorage import (
    ScopeRequirementsValidator,
    TokenStorage,
    TokenValidationError,
    ValidatingTokenStorage,
)

from .authorizer_factory import AuthorizerFactory
from .config import DEFAULT_CONFIG, KNOWN_TOKEN_STORAGES, GlobusAppConfig
from .protocols import TokenStorageProvider


class GlobusApp(metaclass=abc.ABCMeta):
    """
    The abstract base class for managing authentication across services.

    A single ``GlobusApp`` may be bound to many service clients, providing each them
    with dynamically updated authorization tokens. The app is responsible for ensuring
    these tokens are up-to-date and validly scoped; including initiating login flows to
    acquire new tokens when necessary.

    See :class:`UserApp` to oversee interactions with a human.

    See :class:`ClientApp` to oversee interactions with a service account.

    .. warning::

        GlobusApp is **not** thread safe.

    :ivar ValidatingTokenStorage token_storage: The interface used by the app to store,
        retrieve, and validate Globus Auth-issued tokens.
    :ivar dict[str, list[Scope]] scope_requirements: A copy of the app's aggregate scope
        requirements. Modifying the returned dict will not affect the app's internal
        store. To add scope requirements, instead use the :meth:`add_scope_requirements`
        method.
    """

    _login_client: AuthLoginClient
    # a bool is used to track whether or not the AuthorizerFactory is ready for use
    # this allows code during init call into otherwise unsafe codepaths in the app,
    # namely those which manipulate scope requirements
    _authorizer_factory: AuthorizerFactory[GlobusAuthorizer]
    token_storage: ValidatingTokenStorage

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
        self.app_name = app_name
        self.config = config
        self._token_validation_error_handling_enabled = True

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

        # create a consent client for token validation
        # this client won't be ready for immediate use, but will have the app attached
        # at the end of init
        consent_client = AuthClient(environment=config.environment)

        # create the requisite token storage for the app, with validation based on
        # the provided parameters
        self.token_storage = self._initialize_validating_token_storage(
            token_storage=self._token_storage,
            consent_client=consent_client,
            scope_requirements=self._scope_requirements,
        )

        # setup an ID Token Decoder based on config; build one if it was not provided
        self._id_token_decoder = self._initialize_id_token_decoder(
            app_name=self.app_name, config=self.config, login_client=self._login_client
        )

        # initialize our authorizer factory
        self._initialize_authorizer_factory()
        self._authorizer_factory_initialized = True

        # finally, attach the app to the internal consent client
        # this needs to wait until the very end of the app initialization process so
        # that the authorizer factory is all ready to accept the client
        # registering its scope requirements
        #
        # additionally, this will ensure that openid scope requirement is always
        # registered (it's required for token identity validation).
        consent_client.attach_globus_app(self, app_scopes=[Scope(AuthScopes.openid)])

    def _resolve_scope_requirements(
        self, scope_requirements: t.Mapping[str, ScopeCollectionType] | None
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

    def _initialize_validating_token_storage(
        self,
        token_storage: TokenStorage,
        consent_client: AuthClient,
        scope_requirements: t.Mapping[str, t.Sequence[Scope]],
    ) -> ValidatingTokenStorage:
        """
        Initializes the validating token storage for the app.
        """
        validating_token_storage = ValidatingTokenStorage(token_storage)

        # construct ValidatingTokenStorage around the TokenStorage and
        # our initial scope requirements
        scope_validator = ScopeRequirementsValidator(scope_requirements, consent_client)

        # use validators to enforce invariants about scopes
        validating_token_storage.validators.append(scope_validator)

        return validating_token_storage

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
            return token_storage.for_globus_app(
                app_name=app_name,
                config=config,
                client_id=client_id,
                namespace=namespace,
            )

        elif token_storage in KNOWN_TOKEN_STORAGES:
            provider = KNOWN_TOKEN_STORAGES[token_storage]
            return provider.for_globus_app(
                app_name=app_name,
                config=config,
                client_id=client_id,
                namespace=namespace,
            )

        raise GlobusSDKUsageError(
            f"Unsupported token_storage value: {token_storage}. Must be a "
            f"TokenStorage, TokenStorageProvider, or a supported string value."
        )

    def _initialize_id_token_decoder(
        self, *, app_name: str, config: GlobusAppConfig, login_client: AuthLoginClient
    ) -> IDTokenDecoder:
        """
        Create an IDTokenDecoder or use the one provided via config, and set it on
        the token storage adapters.

        It is only set on inner storage if the decoder was not already set, so a
        non-null value won't be overwritten.

        This must run near the end of app initialization, when the `_token_storage`
        (inner) and `token_storage` (validating storage, outer) storages have both
        been initialized.
        """
        if isinstance(self.config.id_token_decoder, IDTokenDecoder):
            id_token_decoder: IDTokenDecoder = self.config.id_token_decoder
        else:
            id_token_decoder = self.config.id_token_decoder.for_globus_app(
                app_name=app_name,
                config=config,
                login_client=login_client,
            )
        if self._token_storage.id_token_decoder is None:
            self._token_storage.id_token_decoder = id_token_decoder
        self.token_storage.id_token_decoder = id_token_decoder

        return id_token_decoder

    @abc.abstractmethod
    def _initialize_authorizer_factory(self) -> None:
        """
        Initializes self._authorizer_factory to be used for generating authorizers to
        authorize requests.
        """

    def login(
        self,
        *,
        auth_params: GlobusAuthorizationParameters | None = None,
        force: bool = False,
    ) -> None:
        """
        Log a user or client into the app, if needed, storing the resulting tokens.

        A login flow will be performed if any of the following are true:
            * The kwarg ``auth_params`` is provided.
            * The kwarg ``force`` is set to True.
            * The method ``self.login_required()`` evaluates to True.

        :param auth_params: An optional set of authorization parameters to establish
            requirements and controls for the login flow.
        :param force: If True, perform a login flow even if one does not appear to
            be necessary.
        """
        if auth_params or force or self.login_required():
            self._run_login_flow(auth_params)

    def login_required(self) -> bool:
        """
        Determine if a login flow will be required to interact with resource servers
        under the current scope requirements.

        This will return false if any of the following are true:
            * Access tokens have never been issued.
            * Access tokens have been issued but have insufficient scopes.
            * Access tokens have expired and wouldn't be resolved with refresh tokens.

        :returns: True if a login flow appears to be required, False otherwise.
        """
        for resource_server in self._scope_requirements.keys():
            try:
                with self._disabled_token_validation_error_handler():
                    self.get_authorizer(resource_server)
            except TokenValidationError:
                return True
        return False

    def logout(self) -> None:
        """
        Log the current user or client out of the app.

        This will remove and revoke all tokens stored for the current app user.
        """
        # Revoke all tokens, removing them from the underlying token storage
        inner_token_storage = self.token_storage.token_storage
        for resource_server in self._scope_requirements.keys():
            token_data = inner_token_storage.get_token_data(resource_server)
            if token_data:
                self._login_client.oauth2_revoke_token(token_data.access_token)
                if token_data.refresh_token:
                    self._login_client.oauth2_revoke_token(token_data.refresh_token)
                inner_token_storage.remove_token_data(resource_server)

        # Invalidate any cached authorizers
        self._authorizer_factory.clear_cache()

    @abc.abstractmethod
    def _run_login_flow(
        self, auth_params: GlobusAuthorizationParameters | None = None
    ) -> None:
        """
        Run an authorization flow to get new tokens which are stored and available
        for the next authorizer gotten by get_authorizer.

        :param auth_params: An optional set of authorization parameters to establish
            requirements and controls for the login flow.
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

    @contextlib.contextmanager
    def _disabled_token_validation_error_handler(self) -> t.Iterator[None]:
        """
        Context manager to disable token validation error handling (as a default)
        for the duration of the context.
        """
        # Record the starting value so we can reset it after the context ends.
        initial_val = self._token_validation_error_handling_enabled

        self._token_validation_error_handling_enabled = False
        try:
            yield
        finally:
            self._token_validation_error_handling_enabled = initial_val

    def add_scope_requirements(
        self, scope_requirements: t.Mapping[str, ScopeCollectionType]
    ) -> None:
        """
        Add given scope requirements to the app's scope requirements. Any duplicate
        requirements will be deduplicated with existing requirements.

        :param scope_requirements: a dict of Scopes indexed by resource server
            that will be added to this app's scope requirements
        """
        for resource_server, scopes in scope_requirements.items():
            curr = self._scope_requirements.setdefault(resource_server, [])
            curr.extend(scopes_to_scope_list(scopes))

        self._authorizer_factory.clear_cache(*scope_requirements.keys())

    def get_authorizer(self, resource_server: str) -> GlobusAuthorizer:
        """
        Get a ``GlobusAuthorizer`` for a resource server.

        This method will be called by service clients while making HTTP requests.

        :param resource_server: The resource server for which the requested Authorizer
            should provide authorization headers.
        """
        error_handling_enabled = self._token_validation_error_handling_enabled

        try:
            # Disable token validation error handling for nested calls.
            # This will ultimately ensure that the error handler is only called once
            # by the root `get_authorizer` invocation.
            with self._disabled_token_validation_error_handler():
                return self._authorizer_factory.get_authorizer(resource_server)
        except TokenValidationError as e:
            if error_handling_enabled and self.config.token_validation_error_handler:
                # Dispatch to the configured error handler if one is set then retry.
                self.config.token_validation_error_handler(self, e)
                return self._authorizer_factory.get_authorizer(resource_server)
            raise e

    @property
    def scope_requirements(self) -> dict[str, list[Scope]]:
        """
        Access a copy of app's aggregate scope requirements.

        Modifying the returned dict will not affect the app's scope requirements.
        To add scope requirements, use ``GlobusApp.add_scope_requirements()``.
        """
        # Scopes are mutable objects so we return a deepcopy
        return copy.deepcopy(self._scope_requirements)
