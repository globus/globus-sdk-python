from __future__ import annotations

import logging
import typing as t

from globus_sdk._types import ScopeCollectionType, UUIDLike
from globus_sdk.authorizers import BasicAuthorizer
from globus_sdk.response import GlobusHTTPResponse

from .._common import stringify_requested_scopes
from ..flow_managers import GlobusAuthorizationCodeFlowManager
from ..response import OAuthDependentTokenResponse, OAuthTokenResponse
from .base import AuthClient

log = logging.getLogger(__name__)


class ConfidentialAppAuthClient(AuthClient):
    """
    This is a specialized type of ``AuthClient`` used to represent an App with
    a Client ID and Client Secret wishing to communicate with Globus Auth.
    It must be given a Client ID and a Client Secret, and furthermore, these
    will be used to establish a :class:`BasicAuthorizer <globus_sdk.BasicAuthorizer>`
    for authorization purposes.
    Additionally, the Client ID is stored for use in various calls.

    Confidential Applications (i.e. Applications which are not Native Apps) are
    those like the `Sample Data Portal
    <https://github.com/globus/globus-sample-data-portal>`_, which have their
    own credentials for authenticating against Globus Auth.

    Any keyword arguments given are passed through to the ``AuthClient``
    constructor.

    .. automethodlist:: globus_sdk.ConfidentialAppAuthClient
    """

    def __init__(
        self,
        client_id: UUIDLike,
        client_secret: str,
        environment: str | None = None,
        base_url: str | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__(
            client_id=client_id,
            authorizer=BasicAuthorizer(str(client_id), client_secret),
            environment=environment,
            base_url=base_url,
            app_name=app_name,
            transport_params=transport_params,
        )

    def oauth2_client_credentials_tokens(
        self,
        requested_scopes: ScopeCollectionType | None = None,
    ) -> OAuthTokenResponse:
        r"""
        Perform an OAuth2 Client Credentials Grant to get access tokens which
        directly represent your client and allow it to act on its own
        (independent of any user authorization).
        This method does not use a ``GlobusOAuthFlowManager`` because it is not
        at all necessary to do so.

        :param requested_scopes: The scopes on the token(s) being requested. Defaults to
            ``openid profile email urn:globus:auth:scope:transfer.api.globus.org:all``
        :type requested_scopes: str, MutableScope, or iterable of str or MutableScope,
            optional
        :rtype: :class:`OAuthTokenResponse <.OAuthTokenResponse>`

        For example, with a Client ID of "CID1001" and a Client Secret of
        "RAND2002", you could use this grant type like so:

        >>> client = ConfidentialAppAuthClient("CID1001", "RAND2002")
        >>> tokens = client.oauth2_client_credentials_tokens()
        >>> transfer_token_info = (
        ...     tokens.by_resource_server["transfer.api.globus.org"])
        >>> transfer_token = transfer_token_info["access_token"]
        """
        log.info("Fetching token(s) using client credentials")
        requested_scopes_string = stringify_requested_scopes(requested_scopes)
        return self.oauth2_token(
            {"grant_type": "client_credentials", "scope": requested_scopes_string}
        )

    def oauth2_start_flow(
        self,
        redirect_uri: str,
        requested_scopes: ScopeCollectionType | None = None,
        *,
        state: str = "_default",
        refresh_tokens: bool = False,
    ) -> GlobusAuthorizationCodeFlowManager:
        """
        Starts or resumes an Authorization Code OAuth2 flow.

        Under the hood, this is done by instantiating a
        :class:`GlobusAuthorizationCodeFlowManager
        <.GlobusAuthorizationCodeFlowManager>`

        :param redirect_uri: The page that users should be directed to after
            authenticating at the authorize URL.
        :type redirect_uri: str
            ``redirect_uri`` (*string*)
        :param requested_scopes: The scopes on the token(s) being requested. Defaults to
            ``openid profile email urn:globus:auth:scope:transfer.api.globus.org:all``
        :type requested_scopes: str, MutableScope, or iterable of str or MutableScope,
            optional
        :param state: This string allows an application to pass information back to
            itself in the course of the OAuth flow. Because the user will navigate away
            from the application to complete the flow, this parameter lets the app pass
            an arbitrary string from the starting page to the ``redirect_uri``
        :type state: str, optional
        :param refresh_tokens: When True, request refresh tokens in addition to access
            tokens. [Default: ``False``]
        :type refresh_tokens: bool, optional

        .. tab-set::

            .. tab-item:: Example Usage

                You can see an example of this flow :ref:`in the usage examples
                <examples_three_legged_oauth_login>`.

            .. tab-item:: API Info

                The Authorization Code Grant flow is described
                `in the Globus Auth Specification
                <https://docs.globus.org/api/auth/developer-guide/#obtaining-authorization>`_.
        """
        log.info("Starting OAuth2 Authorization Code Grant Flow")
        self.current_oauth2_flow_manager = GlobusAuthorizationCodeFlowManager(
            self,
            redirect_uri,
            requested_scopes=requested_scopes,
            state=state,
            refresh_tokens=refresh_tokens,
        )
        return self.current_oauth2_flow_manager

    def oauth2_get_dependent_tokens(
        self,
        token: str,
        *,
        refresh_tokens: bool = False,
        additional_params: dict[str, t.Any] | None = None,
    ) -> OAuthDependentTokenResponse:
        """
        Does a `Dependent Token Grant
        <https://docs.globus.org/api/auth/reference/#dependent_token_grant_post_v2_oauth2_token>`_
        against Globus Auth.
        This exchanges a token given to this client for a new set of tokens
        which give it access to resource servers on which it depends.
        This grant type is intended for use by Resource Servers playing out the
        following scenario:

          1. User has tokens for Service A, but Service A requires access to
             Service B on behalf of the user
          2. Service B should not see tokens scoped for Service A
          3. Service A therefore requests tokens scoped only for Service B,
             based on tokens which were originally scoped for Service A...

        In order to do this exchange, the tokens for Service A must have scopes
        which depend on scopes for Service B (the services' scopes must encode
        their relationship). As long as that is the case, Service A can use
        this Grant to get those "Dependent" or "Downstream" tokens for Service B.

        :param token: A Globus Access Token as a string
        :type token: str
        :param refresh_tokens: When True, request dependent refresh tokens in addition
            to access tokens. [Default: ``False``]
        :type refresh_tokens: bool, optional
        :param additional_params: Additional parameters to include in the request body
        :type additional_params: dict, optional
        :rtype: :class:`OAuthDependentTokenResponse <.OAuthDependentTokenResponse>`
        """
        log.info("Getting dependent tokens from access token")
        log.debug(f"additional_params={additional_params}")
        form_data = {
            "grant_type": "urn:globus:auth:grant_type:dependent_token",
            "token": token,
        }
        # the internal parameter is 'access_type', but using the name 'refresh_tokens'
        # is consistent with the rest of the SDK and better communicates expectations
        # back to the user than the OAuth2 spec wording
        if refresh_tokens:
            form_data["access_type"] = "offline"
        if additional_params:
            form_data.update(additional_params)

        return self.oauth2_token(form_data, response_class=OAuthDependentTokenResponse)

    def oauth2_token_introspect(
        self, token: str, *, include: str | None = None
    ) -> GlobusHTTPResponse:
        """
        Get information about a Globus Auth token.

        :param token: An Access Token as a raw string, being evaluated
        :type token: str
        :param include: A value for the ``include`` parameter in the request body.
            Default is to omit the parameter.
        :type include: str, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    ac = globus_sdk.ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
                    ac.oauth2_token_introspect("<token_string>")

                Get information about a Globus Auth token including the full identity
                set of the user to whom it belongs

                .. code-block:: python

                    ac = globus_sdk.ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
                    data = ac.oauth2_token_introspect("<token_string>", include="identity_set")
                    for identity in data["identity_set"]:
                        print('token authenticates for "{}"'.format(identity))

            .. tab-item:: API Info

                ``POST /v2/oauth2/token/introspect``

                .. extdoclink:: Token Introspection
                    :ref: auth/reference/#token_introspection_post_v2_oauth2_token_introspect
        """  # noqa: E501
        log.info("Checking token validity (introspect)")
        body = {"token": token}
        if include is not None:
            body["include"] = include
        return self.post("/v2/oauth2/token/introspect", data=body, encoding="form")
