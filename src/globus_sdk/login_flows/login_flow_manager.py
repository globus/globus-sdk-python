from __future__ import annotations

import abc

import globus_sdk
from globus_sdk.gare import GlobusAuthorizationParameters


class LoginFlowManager(metaclass=abc.ABCMeta):
    """
    The abstract base class defining the interface for managing login flows.

    Implementing classes must supply a ``run_login_flow`` method.
    Utility functions starting an authorization-code grant flow and getting an
    authorization-code URL are provided on the class.

    :ivar AuthLoginClient login_client: A native or confidential login client to be
        used by the login flow manager.
    :ivar bool request_refresh_tokens: A signal of whether refresh tokens are expected
        to be requested, in addition to access tokens.
    :ivar str native_prefill_named_grant: A string to prefill in a Native App login
        flow. This value is only to be used if the `login_client` is a native client.
    """

    def __init__(
        self,
        login_client: globus_sdk.AuthLoginClient,
        *,
        request_refresh_tokens: bool = False,
        native_prefill_named_grant: str | None = None,
    ) -> None:
        if not isinstance(
            login_client,
            (globus_sdk.NativeAppAuthClient, globus_sdk.ConfidentialAppAuthClient),
        ):
            raise globus_sdk.GlobusSDKUsageError(
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
            session_message=auth_parameters.session_message,
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
        if isinstance(login_client, globus_sdk.NativeAppAuthClient):
            login_client.oauth2_start_flow(
                requested_scopes,
                redirect_uri=redirect_uri,
                refresh_tokens=self.request_refresh_tokens,
                prefill_named_grant=self.native_prefill_named_grant,
            )
        elif isinstance(login_client, globus_sdk.ConfidentialAppAuthClient):
            login_client.oauth2_start_flow(
                redirect_uri,
                requested_scopes,
                refresh_tokens=self.request_refresh_tokens,
            )

    @abc.abstractmethod
    def run_login_flow(
        self,
        auth_parameters: GlobusAuthorizationParameters,
    ) -> globus_sdk.OAuthTokenResponse:
        """
        Run a login flow to get tokens for a user.

        :param auth_parameters: ``GlobusAuthorizationParameters`` passed through
            to the authentication flow to control how the user will authenticate.
        """
