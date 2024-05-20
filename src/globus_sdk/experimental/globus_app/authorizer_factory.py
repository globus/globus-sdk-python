from __future__ import annotations

import abc
import typing as t

from globus_sdk import AuthLoginClient, ConfidentialAppAuthClient
from globus_sdk.authorizers import (
    AccessTokenAuthorizer,
    ClientCredentialsAuthorizer,
    GlobusAuthorizer,
    RefreshTokenAuthorizer,
)
from globus_sdk.experimental.tokenstorage import TokenData
from globus_sdk.services.auth import OAuthTokenResponse

from ._validating_token_storage import ValidatingTokenStorage
from .errors import MissingTokensError

GA = t.TypeVar("GA", bound=GlobusAuthorizer)


class AuthorizerFactory(
    t.Generic[GA],
    metaclass=abc.ABCMeta,
):
    """
    An ``AuthorizerFactory`` is an interface for getting some class of
    ``GlobusAuthorizer`` from a ``ValidatingTokenStorage`` that meets the
    authorization requirements used to initialize the ``ValidatingTokenStorage``.

    An ``AuthorizerFactory`` keeps a cache of authorizer objects that are
    re-used until its ``store_token_response`` method is called.
    """

    def __init__(self, token_storage: ValidatingTokenStorage):
        """
        :param token_storage: The ``ValidatingTokenStorage`` used
        for defining and validating the set of authorization requirements that
        constructed authorizers will meet and accessing underlying token storage
        """
        self.token_storage = token_storage
        self._authorizer_cache: dict[str, GA] = {}

    def _get_token_data_or_error(self, resource_server: str) -> TokenData:
        token_data = self.token_storage.get_token_data(resource_server)
        if token_data is None:
            raise MissingTokensError(f"No token data for {resource_server}")

        return token_data

    def store_token_response_and_clear_cache(
        self, token_res: OAuthTokenResponse
    ) -> None:
        """
        Store a token response in the underlying ``ValidatingTokenStorage``
        and clear the authorizer cache.

        This should not be called when a ``RenewingAuthorizer`` created by this factory
        gets new tokens for itself as there is no need to clear the cache.

        :param token_res: An ``OAuthTokenResponse`` containing token data to be stored
            in the underlying ``ValidatingTokenStorage``.
        """
        self.token_storage.store_token_response(token_res)
        self._authorizer_cache = {}

    def get_authorizer(self, resource_server: str) -> GA:
        """
        Either retrieve a cached authorizer for the given resource server or construct
        a new one if none is cached.

        Raises ``MissingTokensError`` if the underlying ``TokenStorage`` does not
        have the needed tokens to create the authorizer.

        :param resource_server: The resource server the authorizer will produce
            authentication for
        """
        if resource_server in self._authorizer_cache:
            return self._authorizer_cache[resource_server]

        new_authorizer = self._make_authorizer(resource_server)
        self._authorizer_cache[resource_server] = new_authorizer
        return new_authorizer

    @abc.abstractmethod
    def _make_authorizer(self, resource_server: str) -> GA:
        """
        Construct the ``GlobusAuthorizer`` class specific to this ``AuthorizerFactory``

        :param resource_server: The resource server the authorizer will produce
            authentication for
        """


class AccessTokenAuthorizerFactory(AuthorizerFactory[AccessTokenAuthorizer]):
    """
    An ``AuthorizerFactory`` that constructs ``AccessTokenAuthorizer``.
    """

    def _make_authorizer(self, resource_server: str) -> AccessTokenAuthorizer:
        """
        Construct an ``AccessTokenAuthorizer`` for the given resource server.

        Raises ``MissingTokensError`` if the underlying ``TokenStorage`` does not
        have token data for the given resource server.

        :param resource_server: The resource server the authorizer will produce
            authentication for
        """
        token_data = self._get_token_data_or_error(resource_server)
        return AccessTokenAuthorizer(token_data.access_token)


class RefreshTokenAuthorizerFactory(AuthorizerFactory[RefreshTokenAuthorizer]):
    """
    An ``AuthorizerFactory`` that constructs ``RefreshTokenAuthorizer``.
    """

    def __init__(
        self,
        token_storage: ValidatingTokenStorage,
        auth_login_client: AuthLoginClient,
    ):
        """
        :param token_storage: The ``ValidatingTokenStorage`` used
        for defining and validating the set of authorization requirements that
        constructed authorizers will meet and accessing underlying token storage
        :auth_login_client: The ``AuthLoginCLient` used for refreshing tokens with
            Globus Auth
        """
        self.auth_login_client = auth_login_client
        super().__init__(token_storage)

    def _make_authorizer(self, resource_server: str) -> RefreshTokenAuthorizer:
        """
        Construct a ``RefreshTokenAuthorizer`` for the given resource server.

        Raises ``MissingTokensError`` if the underlying ``TokenStorage`` does not
        have a refresh token for the given resource server.

        :param resource_server: The resource server the authorizer will produce
            authentication for
        """
        token_data = self._get_token_data_or_error(resource_server)
        if token_data.refresh_token is None:
            raise MissingTokensError(f"No refresh_token for {resource_server}")

        return RefreshTokenAuthorizer(
            refresh_token=token_data.refresh_token,
            auth_client=self.auth_login_client,
            access_token=token_data.access_token,
            expires_at=token_data.expires_at_seconds,
            on_refresh=self.token_storage.store_token_response,
        )


class ClientCredentialsAuthorizerFactory(
    AuthorizerFactory[ClientCredentialsAuthorizer]
):
    """
    An ``AuthorizerFactory`` that constructs ``ClientCredentialsAuthorizer``.
    """

    def __init__(
        self,
        token_storage: ValidatingTokenStorage,
        confidential_client: ConfidentialAppAuthClient,
    ):
        """
        :param token_storage: The ``ValidatingTokenStorage`` used
        for defining and validating the set of authorization requirements that
        constructed authorizers will meet and accessing underlying token storage
        :param confidential_client: The ``ConfidentialAppAuthClient`` that will
            get client credentials tokens from Globus Auth to act as itself
        """
        self.confidential_client = confidential_client
        super().__init__(token_storage)

    def _make_authorizer(
        self,
        resource_server: str,
    ) -> ClientCredentialsAuthorizer:
        """
        Construct a ``ClientCredentialsAuthorizer`` for the given resource server.

        Does not require that tokens exist in the token storage but will use them if
        present.

        :param resource_server: The resource server the authorizer will produce
            authentication for. The ``ValidatingTokenStorage`` used to create the
            ``ClientCredentialsAuthorizerFactory`` must have scope requirements defined
            for this resource server.
        """
        token_data = self.token_storage.get_token_data(resource_server)
        access_token = token_data.access_token if token_data else None
        expires_at = token_data.expires_at_seconds if token_data else None

        scopes = self.token_storage.scope_requirements.get(resource_server)
        if scopes is None:
            raise ValueError(
                "ValidatingTokenStorage has no scope_requirements for "
                f"resource_server {resource_server}"
            )

        return ClientCredentialsAuthorizer(
            confidential_client=self.confidential_client,
            scopes=scopes,
            access_token=access_token,
            expires_at=expires_at,
            on_refresh=self.token_storage.store_token_response,
        )
