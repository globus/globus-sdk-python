from __future__ import annotations

import abc

from globus_sdk import (
    AuthLoginClient,
    ConfidentialAppAuthClient,
    GlobusSDKUsageError,
    NativeAppAuthClient,
    OAuthTokenResponse,
)
from globus_sdk.experimental.auth_requirements_error import (
    GlobusAuthorizationParameters,
)


class LoginFlowManager(metaclass=abc.ABCMeta):
    """
    A ``LoginFlowManager`` is an abstract superclass for subclasses that manage
    interactive login flows with a user in order to authenticate with Globus Auth
    and obtain tokens.
    """

    def __init__(
        self,
        login_client: AuthLoginClient,
        *,
        request_refresh_tokens: bool = False,
        native_prefill_named_grant: str | None = None,
    ):
        """
        :param login_client: The client to use for login flows.
        :param request_refresh_tokens: Control whether refresh tokens will be requested.
        :param native_prefill_named_grant: The name of a prefill in a Native App login
            flow. This value will be ignored if the login_client is not a
            NativeAppAuthClient.
        """
        if not isinstance(login_client, NativeAppAuthClient) and not isinstance(
            login_client, ConfidentialAppAuthClient
        ):
            raise GlobusSDKUsageError(
                f"{type(self).__name__} requires a NativeAppAuthClient or "
                f"ConfidentialAppAuthClient, but got a {type(login_client).__name__}."
            )

        self.login_client = login_client
        self.request_refresh_tokens = request_refresh_tokens
        self.native_prefill_named_grant = native_prefill_named_grant

    def _get_authorize_url(
        self, auth_parameters: GlobusAuthorizationParameters, redirect_uri: str
    ) -> str:
        """
        Utility method to provide a simpler interface for subclasses to start an
        authorization flow and get an authorization URL.
        """
        self._oauth2_start_flow(auth_parameters, redirect_uri)

        session_required_single_domain = auth_parameters.session_required_single_domain
        return self.login_client.oauth2_get_authorize_url(
            session_required_identities=auth_parameters.session_required_identities,
            session_required_single_domain=session_required_single_domain,
            session_required_policies=auth_parameters.session_required_policies,
            session_required_mfa=auth_parameters.session_required_mfa,
            prompt=auth_parameters.prompt,  # type: ignore
        )

    def _oauth2_start_flow(
        self, auth_parameters: GlobusAuthorizationParameters, redirect_uri: str
    ) -> None:
        """
        Start an authorization flow with the class's login_client, returning an
        authorization URL to direct a user to.
        """
        login_client = self.login_client
        requested_scopes = auth_parameters.required_scopes
        # Native and Confidential App clients have different signatures for this method,
        # so they must be type checked & called independently.
        if isinstance(login_client, NativeAppAuthClient):
            login_client.oauth2_start_flow(
                requested_scopes,
                redirect_uri=redirect_uri,
                refresh_tokens=self.request_refresh_tokens,
                prefill_named_grant=self.native_prefill_named_grant,
            )
        elif isinstance(login_client, ConfidentialAppAuthClient):
            login_client.oauth2_start_flow(
                redirect_uri,
                requested_scopes,
                refresh_tokens=self.request_refresh_tokens,
            )

    @abc.abstractmethod
    def run_login_flow(
        self,
        auth_parameters: GlobusAuthorizationParameters,
    ) -> OAuthTokenResponse:
        """
        Run an interactive login flow to get tokens for the user.

        :param auth_parameters: ``GlobusAuthorizationParameters`` passed through
            to the authentication flow to control how the user will authenticate.
        """
