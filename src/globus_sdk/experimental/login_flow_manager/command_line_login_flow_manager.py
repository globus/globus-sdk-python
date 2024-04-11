from globus_sdk import AuthLoginClient, OAuthTokenResponse
from globus_sdk.experimental.auth_requirements_error import (
    GlobusAuthorizationParameters,
)

from .login_flow_manager import LoginFlowManager


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
        refresh_tokens: bool = False,
        login_prompt: str = "Please authenticate with Globus here:",
        code_prompt: str = "Enter the resulting Authorization Code here:",
    ):
        """
        :param login_client: The ``AuthLoginClient`` that will be making the Globus
            Auth API calls needed for the authentication flow. Note that this
            must either be a NativeAppAuthClient or a templated
            ConfidentialAppAuthClient, standard ConfidentialAppAuthClients cannot
            use the web auth-code flow.
        :param refresh_tokens: Control whether refresh tokens will be requested.
        :param login_prompt: The string that will be output to the command line
            prompting the user to authenticate.
        :param code_prompt: The string that will be output to the command line
            prompting the user to enter their authorization code.
        """
        self.login_prompt = login_prompt
        self.code_prompt = code_prompt
        super().__init__(login_client, refresh_tokens=refresh_tokens)

    def run_login_flow(
        self,
        auth_parameters: GlobusAuthorizationParameters,
    ) -> OAuthTokenResponse:
        """
        Run an interactive login flow on the command line to get tokens for the user.

        :param auth_parameters: ``GlobusAuthorizationParameters`` passed through
            to the authentication flow to control how the user will authenticate.
        """

        # type is ignored here as AuthLoginClient does not provide a signature for
        # oauth2_start_flow since it has different positional arguments between
        # NativeAppAuthClient and ConfidentialAppAuthClient
        self.login_client.oauth2_start_flow(  # type: ignore
            redirect_uri=self.login_client.base_url + "v2/web/auth-code",
            refresh_tokens=self.refresh_tokens,
            requested_scopes=auth_parameters.required_scopes,
        )

        # create authorization url and prompt user to follow it to login
        print(
            "{0}\n{1}\n{2}\n{1}\n".format(
                self.login_prompt,
                "-" * len(self.login_prompt),
                self.login_client.oauth2_get_authorize_url(
                    session_required_identities=(
                        auth_parameters.session_required_identities
                    ),
                    session_required_single_domain=(
                        auth_parameters.session_required_single_domain
                    ),
                    session_required_policies=auth_parameters.session_required_policies,
                    session_required_mfa=auth_parameters.session_required_mfa,
                    prompt=auth_parameters.prompt,  # type: ignore
                ),
            )
        )

        # ask user to copy and paste auth code
        auth_code = input(f"{self.code_prompt}\n").strip()

        # get and return tokens
        return self.login_client.oauth2_exchange_code_for_tokens(auth_code)
