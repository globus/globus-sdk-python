from __future__ import annotations

import textwrap
import typing as t
from contextlib import contextmanager

import globus_sdk
from globus_sdk._utils import get_nice_hostname
from globus_sdk.exc.base import GlobusError
from globus_sdk.gare import GlobusAuthorizationParameters

from .login_flow_manager import LoginFlowManager

if t.TYPE_CHECKING:
    from globus_sdk.globus_app import GlobusAppConfig


class CommandLineLoginFlowEOFError(GlobusError, EOFError):
    """
    An error raised when a CommandLineLoginFlowManager reads an EOF when prompting for
    a code.
    """


class CommandLineLoginFlowManager(LoginFlowManager):
    """
    A login flow manager which drives authorization-code token grants through the
    command line.

    :param AuthLoginClient login_client: The client that will be making Globus
        Auth API calls required for a login flow.

        .. note::
            If this client is a :class:`globus_sdk.ConfidentialAppAuthClient`, an
            explicit `redirect_uri` param is required.

    :param str redirect_uri: The redirect URI to use for the login flow. When the
        `login_client` is a native client, this defaults to a Globus-hosted URL.
    :param bool request_refresh_tokens: A signal of whether refresh tokens are expected
        to be requested, in addition to access tokens.
    :param str native_prefill_named_grant: A string to prefill in a Native App login
        flow. This value is only used if the `login_client` is a native client.
    """

    def __init__(
        self,
        login_client: globus_sdk.AuthLoginClient,
        *,
        redirect_uri: str | None = None,
        request_refresh_tokens: bool = False,
        native_prefill_named_grant: str | None = None,
    ) -> None:
        super().__init__(
            login_client,
            request_refresh_tokens=request_refresh_tokens,
            native_prefill_named_grant=native_prefill_named_grant,
        )

        if redirect_uri is None:
            # Confidential clients must always define their own custom redirect URI.
            if isinstance(login_client, globus_sdk.ConfidentialAppAuthClient):
                msg = "Use of a Confidential client requires an explicit redirect_uri."
                raise globus_sdk.GlobusSDKUsageError(msg)

            # Native clients may infer the globus-provided helper page if omitted.
            redirect_uri = login_client.base_url + "v2/web/auth-code"
        self.redirect_uri = redirect_uri

    @classmethod
    def for_globus_app(
        cls,
        app_name: str,
        login_client: globus_sdk.AuthLoginClient,
        config: GlobusAppConfig,
    ) -> CommandLineLoginFlowManager:
        """
        Create a ``CommandLineLoginFlowManager`` for use in a GlobusApp.

        :param app_name: The name of the app. Will be prefilled in native auth flows.
        :param login_client: A client used to make Globus Auth API calls.
        :param config: A GlobusApp-bounded object used to configure login flow manager.
        :raises GlobusSDKUsageError: if login_redirect_uri is not set on the config
            but a ConfidentialAppAuthClient is supplied.
        """
        hostname = get_nice_hostname()
        if hostname:
            prefill = f"{app_name} on {hostname}"
        else:
            prefill = app_name

        return cls(
            login_client,
            redirect_uri=config.login_redirect_uri,
            request_refresh_tokens=config.request_refresh_tokens,
            native_prefill_named_grant=prefill,
        )

    def run_login_flow(
        self,
        auth_parameters: GlobusAuthorizationParameters,
    ) -> globus_sdk.OAuthTokenResponse:
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

        :returns: The authorization code entered by the user.
        """
        code_prompt = "Enter the resulting Authorization Code here: "
        with self._handle_input_errors():
            return input(code_prompt).strip()

    @contextmanager
    def _handle_input_errors(self) -> t.Iterator[None]:
        try:
            yield
        except EOFError as e:
            msg = (
                "An EOF was read when an authorization code was expected."
                " (Are you running this in an interactive terminal?)"
            )
            raise CommandLineLoginFlowEOFError(msg) from e
