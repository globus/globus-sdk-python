from __future__ import annotations

import textwrap
import typing as t

from globus_sdk import (
    AuthLoginClient,
    ConfidentialAppAuthClient,
    GlobusSDKUsageError,
    OAuthTokenResponse,
)
from globus_sdk.gare import GlobusAuthorizationParameters

from .login_flow_manager import LoginFlowManager

if t.TYPE_CHECKING:
    from globus_sdk.experimental.globus_app import GlobusAppConfig


class CommandLineLoginFlowManager(LoginFlowManager):
    """
    A ``CommandLineLoginFlowManager`` is a ``LoginFlowManager`` that uses the command
    line for interacting with the user during its interactive login flows.

    Example usage:

    >>> login_client = globus_sdk.NativeAppAuthClient(...)
    >>> login_flow_manager = CommandLineLoginFlowManager(login_client)
    >>> scopes = [globus_sdk.scopes.TransferScopes.all]
    >>> auth_params = GlobusAuthorizationParameters(required_scopes=scopes)
    >>> tokens = login_flow_manager.run_login_flow(auth_params)

    """

    def __init__(
        self,
        login_client: AuthLoginClient,
        *,
        redirect_uri: str | None = None,
        request_refresh_tokens: bool = False,
        native_prefill_named_grant: str | None = None,
    ) -> None:
        """
        :param login_client: The ``AuthLoginClient`` that will be making the Globus
            Auth API calls needed for the authentication flow. Note that this
            must either be a NativeAppAuthClient or a templated
            ConfidentialAppAuthClient, standard ConfidentialAppAuthClients cannot
            use the web auth-code flow.
        :param redirect_uri: The redirect URI to use for the login flow. Defaults to
            a globus-hosted helper web auth-code URI for NativeAppAuthClients.
        :param request_refresh_tokens: Control whether refresh tokens will be requested.
        :param native_prefill_named_grant: The named grant label to prefill on the
            consent page when using a NativeAppAuthClient.
        """
        super().__init__(
            login_client,
            request_refresh_tokens=request_refresh_tokens,
            native_prefill_named_grant=native_prefill_named_grant,
        )

        if redirect_uri is None:
            # Confidential clients must always define their own custom redirect URI.
            if isinstance(login_client, ConfidentialAppAuthClient):
                msg = "Use of a Confidential client requires an explicit redirect_uri."
                raise GlobusSDKUsageError(msg)

            # Native clients may infer the globus-provided helper page if omitted.
            redirect_uri = login_client.base_url + "v2/web/auth-code"
        self.redirect_uri = redirect_uri

    @classmethod
    def for_globus_app(
        cls, app_name: str, login_client: AuthLoginClient, config: GlobusAppConfig
    ) -> CommandLineLoginFlowManager:
        """
        Create a ``CommandLineLoginFlowManager`` for a given ``GlobusAppConfig``.

        :param app_name: The name of the app to use for prefilling the named grant in
            native auth flows.
        :param login_client: The ``AuthLoginClient`` to use to drive Globus Auth flows.
        :param config: A ``GlobusAppConfig`` to configure the login flow.
        :returns: A ``CommandLineLoginFlowManager`` instance.
        :raises: GlobusSDKUsageError if a login_redirect_uri is not set on the config
            but a ConfidentialAppAuthClient is used.
        """
        return cls(
            login_client,
            redirect_uri=config.login_redirect_uri,
            request_refresh_tokens=config.request_refresh_tokens,
            native_prefill_named_grant=app_name,
        )

    def run_login_flow(
        self,
        auth_parameters: GlobusAuthorizationParameters,
    ) -> OAuthTokenResponse:
        """
        Run an interactive login flow on the command line to get tokens for the user.

        :param auth_parameters: ``GlobusAuthorizationParameters`` passed through
            to the authentication flow to control how the user will authenticate.
        """
        authorize_url = self._get_authorize_url(auth_parameters, self.redirect_uri)
        self.print_authorize_url(authorize_url)
        auth_code = self.prompt_for_code()

        return self.login_client.oauth2_exchange_code_for_tokens(auth_code)

    def print_authorize_url(self, authorize_url: str) -> None:
        """
        Prompt the user to authenticate using the provided ``authorize_url``.

        :param authorize_url: The URL at which the user will login and consent to
            application accesses.
        """
        login_prompt = "Please authenticate with Globus here:"
        print(
            textwrap.dedent(
                f"""
                {login_prompt}
                {"-" * len(login_prompt)}
                {authorize_url}
                {"-" * len(login_prompt)}
                """
            )
        )

    def prompt_for_code(self) -> str:
        """
        Prompt the user to enter an authorization code.
        """
        code_prompt = "Enter the resulting Authorization Code here: "
        return input(code_prompt).strip()
