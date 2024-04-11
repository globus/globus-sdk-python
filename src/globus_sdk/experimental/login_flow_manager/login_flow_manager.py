import abc

from globus_sdk import AuthLoginClient, OAuthTokenResponse
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
        refresh_tokens: bool = False,
    ):
        self.login_client = login_client
        self.refresh_tokens = refresh_tokens
        """
        :param refresh_tokens: Control whether refresh tokens will be requested.
        """

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
