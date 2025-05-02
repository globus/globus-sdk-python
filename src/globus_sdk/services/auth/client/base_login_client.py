from __future__ import annotations

import logging
import typing as t

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from globus_sdk import _guards, client, exc, utils
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer, NullAuthorizer
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import AuthScopes, Scope

from .._common import get_jwk_data, pem_decode_jwk_data
from ..errors import AuthAPIError
from ..flow_managers import GlobusOAuthFlowManager
from ..response import (
    OAuthAuthorizationCodeResponse,
    OAuthRefreshTokenResponse,
    OAuthTokenResponse,
)

log = logging.getLogger(__name__)

RT = t.TypeVar("RT", bound=GlobusHTTPResponse)


class AuthLoginClient(client.BaseClient):
    """
    This client class provides the common base for clients providing login
    functionality via
    `Globus Auth <https://docs.globus.org/api/auth/>`_

    :param client_id: The ID of the application provided by registration with
        Globus Auth.

    All other initialization parameters are passed through to ``BaseClient``.

    .. automethodlist:: globus_sdk.AuthLoginClient
    """

    service_name = "auth"
    error_class = AuthAPIError
    scopes = AuthScopes

    def __init__(
        self,
        client_id: UUIDLike | None = None,
        environment: str | None = None,
        base_url: str | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__(
            environment=environment,
            base_url=base_url,
            authorizer=authorizer,
            app_name=app_name,
            transport_params=transport_params,
        )
        self.client_id: str | None = str(client_id) if client_id is not None else None
        # an AuthClient may contain a GlobusOAuth2FlowManager in order to
        # encapsulate the functionality of various different types of flow
        # managers
        self.current_oauth2_flow_manager: GlobusOAuthFlowManager | None = None

        log.debug(
            "Finished initializing AuthLoginClient. "
            f"client_id='{client_id}', type(authorizer)={type(authorizer)}"
        )

    @property
    def default_scope_requirements(self) -> list[Scope]:
        raise exc.GlobusSDKUsageError(
            "AuthLoginClients do not have default_scope_requirements, "
            "use AuthClient instead."
        )

    # FYI: this get_openid_configuration method is duplicated in AuthClient
    # if this code is modified, please update that copy as well
    #
    # we would like to restructure code using this method to be calling the matching
    # AuthClient method
    # for example, a future SDK version may make an AuthLoginClient contain
    # an AuthClient which it uses
    def get_openid_configuration(self) -> GlobusHTTPResponse:
        """
        Fetch the OpenID Connect configuration data from the well-known URI for Globus
        Auth.
        """
        log.debug("Fetching OIDC Config")
        return self.get("/.well-known/openid-configuration")

    @t.overload
    def get_jwk(
        self,
        openid_configuration: None | GlobusHTTPResponse | dict[str, t.Any],
        *,
        as_pem: t.Literal[True],
    ) -> RSAPublicKey: ...

    @t.overload
    def get_jwk(
        self,
        openid_configuration: None | GlobusHTTPResponse | dict[str, t.Any],
        *,
        as_pem: t.Literal[False],
    ) -> dict[str, t.Any]: ...

    # FYI: this get_jwk method is duplicated in AuthClient
    # if this code is modified, please update that copy as well
    #
    # we would like to restructure code using this method to be calling the matching
    # AuthClient method
    # for example, a future SDK version may make an AuthLoginClient contain
    # an AuthClient which it uses
    def get_jwk(
        self,
        openid_configuration: None | GlobusHTTPResponse | dict[str, t.Any] = None,
        *,
        as_pem: bool = False,
    ) -> RSAPublicKey | dict[str, t.Any]:
        """
        Fetch the Globus Auth JWK.

        Returns either a dict or an RSA Public Key object depending on ``as_pem``.

        :param openid_configuration: The OIDC config as a GlobusHTTPResponse or dict.
            When not provided, it will be fetched automatically.
        :param as_pem: Decode the JWK to an RSA PEM key, typically for JWT decoding
        """
        if openid_configuration is None:
            log.debug("No OIDC Config provided, autofetching...")
            openid_configuration = self.get_openid_configuration()
        jwk_data = get_jwk_data(
            fget=self.get, openid_configuration=openid_configuration
        )
        return pem_decode_jwk_data(jwk_data=jwk_data) if as_pem else jwk_data

    def oauth2_get_authorize_url(
        self,
        *,
        session_required_identities: UUIDLike | t.Iterable[UUIDLike] | None = None,
        session_required_single_domain: str | t.Iterable[str] | None = None,
        session_required_policies: UUIDLike | t.Iterable[UUIDLike] | None = None,
        session_required_mfa: bool | None = None,
        session_message: str | None = None,
        prompt: t.Literal["login"] | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> str:
        """
        Get the authorization URL to which users should be sent.
        This method may only be called after ``oauth2_start_flow``
        has been called on this ``AuthClient``.

        :param session_required_identities: A list of identities must be
            added to the session.
        :param session_required_single_domain: A list of domain requirements
            which must be satisfied by identities added to the session.
        :param session_required_policies: A list of IDs for policies which must
            be satisfied by the user.
        :param session_required_mfa: Whether MFA is required for the session.
        :param session_message: A message to be displayed to the user by Globus Auth.
        :param prompt:
            Control whether a user is required to log in before the authorization step.

            If set to "login", the user must authenticate with an identity provider
            even if they are already logged in. Setting this parameter can help ensure
            that a user's session meets known or unknown session requirement policies
            and avoid additional login flows.
        :param query_params: Additional query parameters to include in the
            authorize URL. Primarily for internal use
        """
        if not self.current_oauth2_flow_manager:
            log.error("OutOfOrderOperations(get_authorize_url before start_flow)")
            raise exc.GlobusSDKUsageError(
                "Cannot get authorize URL until starting an OAuth2 flow. "
                "Call the oauth2_start_flow() method on this "
                "AuthClient to resolve"
            )
        if query_params is None:
            query_params = {}
        if session_required_identities is not None:
            query_params["session_required_identities"] = utils.commajoin(
                session_required_identities
            )
        if session_required_single_domain is not None:
            query_params["session_required_single_domain"] = utils.commajoin(
                session_required_single_domain
            )
        if session_required_policies is not None:
            query_params["session_required_policies"] = utils.commajoin(
                session_required_policies
            )
        if session_required_mfa is not None:
            query_params["session_required_mfa"] = session_required_mfa
        if session_message is not None:
            query_params["session_message"] = session_message
        if prompt is not None:
            query_params["prompt"] = prompt
        auth_url = self.current_oauth2_flow_manager.get_authorize_url(
            query_params=query_params
        )
        log.debug(f"Got authorization URL: {auth_url}")
        return auth_url

    def oauth2_exchange_code_for_tokens(
        self, auth_code: str
    ) -> OAuthAuthorizationCodeResponse:
        """
        Exchange an authorization code for a token or tokens.

        :param auth_code: An auth code typically obtained by sending the user to the
            authorize URL. The code is a very short-lived credential which this method
            is exchanging for tokens. Tokens are the credentials used to authenticate
            against Globus APIs.
        """
        log.debug(
            "Final Step of 3-legged OAuth2 Flows: "
            "Exchanging authorization code for token(s)"
        )
        if not self.current_oauth2_flow_manager:
            log.error("OutOfOrderOperations(exchange_code before start_flow)")
            raise exc.GlobusSDKUsageError(
                "Cannot exchange auth code until starting an OAuth2 flow. "
                "Call the oauth2_start_flow() method on this "
                "AuthClient to resolve"
            )

        return self.current_oauth2_flow_manager.exchange_code_for_tokens(auth_code)

    def oauth2_refresh_token(
        self,
        refresh_token: str,
        *,
        body_params: dict[str, t.Any] | None = None,
    ) -> OAuthRefreshTokenResponse:
        r"""
        Exchange a refresh token for a
        :class:`OAuthTokenResponse <.OAuthTokenResponse>`, containing
        an access token.

        Does a token call of the form

        .. code-block:: none

            refresh_token=<refresh_token>
            grant_type=refresh_token

        plus any additional parameters you may specify.

        :param refresh_token: A Globus Refresh Token as a string
        :param body_params: A dict of extra params to encode in the refresh call.
        """
        log.debug("Executing token refresh; typically requires client credentials")
        form_data = {"refresh_token": refresh_token, "grant_type": "refresh_token"}
        return self.oauth2_token(
            form_data, body_params=body_params, response_class=OAuthRefreshTokenResponse
        )

    def oauth2_validate_token(
        self,
        token: str,
        *,
        body_params: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Deprecated. Because the validity of a token may be dependent on policies
        enforced both by Globus Auth and the resource server, this method is not
        considered a reliable way to check token validity.
        Users are encouraged to treat tokens as valid until proven otherwise instead.

        :param token: The token which should be validated. Can be a refresh token or an
            access token
        :param body_params: Additional parameters to include in the validation
            body. Primarily for internal use
        """
        exc.warn_deprecated(
            f"{self.__class__.__name__}.oauth2_validate_token() is deprecated. "
            "This validation method gives non-definitive results. "
            "Tokens should be treated as valid until they are used and their "
            "validity can be assessed."
        )
        log.debug("Validating token")
        body = {"token": token}

        # if this client has no way of authenticating itself but
        # it does have a client_id, we'll send that in the request
        no_authentication = _guards.is_optional(self.authorizer, NullAuthorizer)
        if no_authentication and self.client_id:
            log.debug("Validating token with unauthenticated client")
            body.update({"client_id": self.client_id})

        if body_params:
            body.update(body_params)
        return self.post("/v2/oauth2/token/validate", data=body, encoding="form")

    def oauth2_revoke_token(
        self,
        token: str,
        *,
        body_params: dict[str, t.Any] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Revoke a token. It can be an Access Token or a Refresh token.

        This call should be used to revoke tokens issued to your client,
        rendering them inert and not further usable. Typically, this is
        incorporated into "logout" functionality, but it should also be used if
        the client detects that its tokens are in an unsafe location (e.x.
        found in a world-readable logfile).

        You can check the "active" status of the token after revocation if you
        want to confirm that it was revoked.

        :param token: The token which should be revoked
        :param body_params: Additional parameters to include in the revocation
            body, which can help speed the revocation process. Primarily for
            internal use

        **Examples**

        >>> from globus_sdk import ConfidentialAppAuthClient
        >>> ac = ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
        >>> ac.oauth2_revoke_token('<token_string>')
        """
        log.debug("Revoking token")
        body = {"token": token}

        # if this client has no way of authenticating itself but
        # it does have a client_id, we'll send that in the request
        no_authentication = self.authorizer is None or isinstance(
            self.authorizer, NullAuthorizer
        )
        if no_authentication and self.client_id:
            log.debug("Revoking token with unauthenticated client")
            body.update({"client_id": self.client_id})

        if body_params:
            body.update(body_params)
        return self.post("/v2/oauth2/token/revoke", data=body, encoding="form")

    @t.overload
    def oauth2_token(
        self,
        form_data: dict[str, t.Any] | utils.PayloadWrapper,
    ) -> OAuthTokenResponse: ...

    @t.overload
    def oauth2_token(
        self,
        form_data: dict[str, t.Any] | utils.PayloadWrapper,
        *,
        body_params: dict[str, t.Any] | None,
    ) -> OAuthTokenResponse: ...

    @t.overload
    def oauth2_token(
        self,
        form_data: dict[str, t.Any] | utils.PayloadWrapper,
        *,
        response_class: type[RT],
    ) -> RT: ...

    @t.overload
    def oauth2_token(
        self,
        form_data: dict[str, t.Any] | utils.PayloadWrapper,
        *,
        body_params: dict[str, t.Any] | None,
        response_class: type[RT],
    ) -> RT: ...

    def oauth2_token(
        self,
        form_data: dict[str, t.Any] | utils.PayloadWrapper,
        *,
        body_params: dict[str, t.Any] | None = None,
        response_class: type[OAuthTokenResponse] | type[RT] = OAuthTokenResponse,
    ) -> OAuthTokenResponse | RT:
        """
        This is the generic form of calling the OAuth2 Token endpoint.
        It takes ``form_data``, a dict which will be encoded in a form POST
        body on the request.

        Generally, users of the SDK should not call this method unless they are
        implementing OAuth2 flows.

        :param response_class: This is used by calls to the oauth2_token endpoint which
            need to specialize their responses. For example,
            :meth:`oauth2_get_dependent_tokens \
            <globus_sdk.ConfidentialAppAuthClient.oauth2_get_dependent_tokens>`
            requires a specialize response class to handle the dramatically different
            format of the Dependent Token Grant response
        :param form_data: The main body of the request
        :param body_params: Any additional parameters to be passed through
            as body parameters.
        :rtype: ``response_class`` if set, defaults to
            :py:attr:`~globus_sdk.OAuthTokenResponse`
        """
        log.debug("Fetching new token from Globus Auth")
        # use the fact that requests implicitly encodes the `data` parameter as
        # a form POST
        data = dict(form_data)
        if body_params:
            data.update(body_params)
        return response_class(
            self.post(
                "/v2/oauth2/token",
                data=data,
                encoding="form",
            )
        )
