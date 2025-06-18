from __future__ import annotations

import logging
import typing as t
import urllib.parse

from globus_sdk._missing import filter_missing
from globus_sdk._types import ScopeCollectionType
from globus_sdk._utils import slash_join

from .._common import stringify_requested_scopes
from ..response import OAuthAuthorizationCodeResponse
from .base import GlobusOAuthFlowManager

if t.TYPE_CHECKING:
    import globus_sdk

log = logging.getLogger(__name__)


class GlobusAuthorizationCodeFlowManager(GlobusOAuthFlowManager):
    """
    This is the OAuth flow designated for use by Clients wishing to
    authenticate users in a web application backed by a server-side component
    (e.g. an API). The key constraint is that there is a server-side system
    that can keep a Client Secret without exposing it to the web client.
    For example, a Django application can rely on the webserver to own the
    secret, so long as it doesn't embed it in any of the pages it generates.

    The application sends the user to get a temporary credential (an
    ``auth_code``) associated with its Client ID. It then exchanges that
    temporary credential for a token, protecting the exchange with its Client
    Secret (to prove that it really is the application that the user just
    authorized).

    :param auth_client: The client used to extract default values for the flow,
        and also to make calls to the Auth service.
    :param redirect_uri: The page that users should be directed to after authenticating
        at the authorize URL.
    :param requested_scopes: The scopes on the token(s) being requested.
    :param state: This string allows an application to pass information back to itself
        in the course of the OAuth flow. Because the user will navigate away from the
        application to complete the flow, this parameter lets the app pass an arbitrary
        string from the starting page to the ``redirect_uri``
    :param refresh_tokens: When True, request refresh tokens in addition to access
        tokens. [Default: ``False``]
    """

    def __init__(
        self,
        auth_client: globus_sdk.ConfidentialAppAuthClient,
        redirect_uri: str,
        requested_scopes: ScopeCollectionType,
        state: str = "_default",
        refresh_tokens: bool = False,
    ) -> None:
        # convert a scope object or iterable to string immediately on load
        # and default to the default requested scopes
        self.requested_scopes: str = stringify_requested_scopes(requested_scopes)

        # store the remaining parameters directly, with no transformation
        self.client_id = auth_client.client_id
        self.auth_client = auth_client
        self.redirect_uri = redirect_uri
        self.refresh_tokens = refresh_tokens
        self.state = state

        log.debug(
            "Starting Authorization Code Flow with params: "
            f"auth_client.client_id={auth_client.client_id} , "
            f"redirect_uri={redirect_uri} , "
            f"refresh_tokens={refresh_tokens} , "
            f"state={state} , "
            f"requested_scopes={self.requested_scopes}"
        )

    def get_authorize_url(self, query_params: dict[str, t.Any] | None = None) -> str:
        """
        Start a Authorization Code flow by getting the authorization URL to
        which users should be sent.

        :param query_params: Additional parameters to include in the authorize URL.
            Primarily for internal use

        The returned URL string is encoded to be suitable to display to users
        in a link or to copy into their browser. Users will be redirected
        either to your provided ``redirect_uri`` or to the default location,
        with the ``auth_code`` embedded in a query parameter.
        """
        authorize_base_url = slash_join(
            self.auth_client.base_url, "/v2/oauth2/authorize"
        )
        log.debug(f"Building authorization URI. Base URL: {authorize_base_url}")
        log.debug(f"query_params={query_params}")

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.requested_scopes,
            "state": self.state,
            "response_type": "code",
            "access_type": (self.refresh_tokens and "offline") or "online",
            **(query_params or {}),
        }
        params = filter_missing(params)
        encoded_params = urllib.parse.urlencode(params)
        return f"{authorize_base_url}?{encoded_params}"

    def exchange_code_for_tokens(
        self, auth_code: str
    ) -> OAuthAuthorizationCodeResponse:
        """
        The second step of the Authorization Code flow, exchange an
        authorization code for access tokens (and refresh tokens if specified)

        :param auth_code: The short-lived code to exchange for tokens
        """
        log.debug(
            "Performing Authorization Code auth_code exchange. "
            "Sending client_id and client_secret"
        )
        return self.auth_client.oauth2_token(
            {
                "grant_type": "authorization_code",
                "code": auth_code.encode("utf-8"),
                "redirect_uri": self.redirect_uri,
            },
            response_class=OAuthAuthorizationCodeResponse,
        )
