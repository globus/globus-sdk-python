from __future__ import annotations

import os
import threading
import typing as t
import webbrowser
from contextlib import contextmanager
from string import Template

from globus_sdk import AuthLoginClient, OAuthTokenResponse
from globus_sdk.experimental.auth_requirements_error import (
    GlobusAuthorizationParameters,
)

from ._local_server import (
    DEFAULT_HTML_TEMPLATE,
    LocalServerError,
    RedirectHandler,
    RedirectHTTPServer,
)
from .login_flow_manager import LoginFlowManager

# a list of text-only browsers which are not allowed for use because they don't work
# with Globus Auth login flows and seize control of the terminal
#
# see the webbrowser library for a list of names:
#   https://github.com/python/cpython/blob/69cdeeb93e0830004a495ed854022425b93b3f3e/Lib/webbrowser.py#L489-L502
BROWSER_BLACKLIST = ["lynx", "www-browser", "links", "elinks", "w3m"]


class LocalServerLoginFlowError(BaseException):
    """
    Error class for errors raised due to inability to run a local server login flow
    due to known failure conditions such as remote sessions or text-only browsers.
    Catching this should be sufficient to detect cases where one should fallback
    to a CommandLineLoginFlowManager
    """


def _check_remote_session() -> None:
    """
    Try to check if this is being run during a remote session, if so
    raise LocalServerLoginFlowError
    """
    if bool(os.environ.get("SSH_TTY", os.environ.get("SSH_CONNECTION"))):
        raise LocalServerLoginFlowError(
            "Cannot use LocalServerLoginFlowManager in a remote session"
        )


def _open_webbrowser(url: str) -> None:
    """
    Get a default browser and open given url
    If browser is known to be text-only, or opening fails, raise
    LocalServerLoginFlowError
    """
    try:
        browser = webbrowser.get()
        if browser.name in BROWSER_BLACKLIST:
            raise LocalServerLoginFlowError(
                "Cannot use LocalServerLoginFlowManager with "
                f"text-only browser '{browser.name}'"
            )

        if not browser.open(url, new=1):
            raise LocalServerLoginFlowError("Failed to open browser '{browser.name}'")
    except webbrowser.Error as exc:
        raise LocalServerLoginFlowError("Failed to open browser") from exc


class LocalServerLoginFlowManager(LoginFlowManager):
    """
    A ``LocalServerLoginFlowManager`` is a ``LoginFlowManager`` that uses a locally
    hosted server to automatically receive the auth code from Globus auth after the
    user has authenticated.

    Example usage:

    >>> login_client = globus_sdk.NativeAppAuthClient(...)
    >>> login_flow_manager = LocalServerLoginFlowManager(login_client)
    >>> scopes = [globus_sdk.scopes.TransferScopes.all]
    >>> auth_params = GlobusAuthorizationParameters(required_scopes=scopes)
    >>> tokens = login_flow_manager.run_login_flow(auth_params)

    """

    def __init__(
        self,
        login_client: AuthLoginClient,
        *,
        refresh_tokens: bool = False,
        server_address: tuple[str, int] = ("127.0.0.1", 0),
        html_template: Template = DEFAULT_HTML_TEMPLATE,
    ):
        """
        :param login_client: The ``AuthLoginClient`` that will be making the Globus
            Auth API calls needed for the authentication flow. Note that this
            must either be a NativeAppAuthClient or a templated
            ConfidentialAppAuthClient, standard ConfidentialAppAuthClients cannot
            use the web auth-code flow.
        :param refresh_tokens: Control whether refresh tokens will be requested.
        :param html_template: Optional HTML Template to be populated with the values
            login_result and post_login_message and displayed to the user.
        :param server_address: Optional tuple of the form (host, port) to specify an
            address to run the local server at.
        """
        self.server_address = server_address
        self.html_template = html_template
        super().__init__(login_client, refresh_tokens=refresh_tokens)

    def run_login_flow(
        self,
        auth_parameters: GlobusAuthorizationParameters,
    ) -> OAuthTokenResponse:
        """
        Run an interactive login flow using a locally hosted server to get tokens
        for the user.

        :param auth_parameters: ``GlobusAuthorizationParameters`` passed through
            to the authentication flow to control how the user will authenticate.
        """
        _check_remote_session()

        with self.start_local_server() as server:
            host, port = server.socket.getsockname()
            redirect_uri = f"http://{host}:{port}"

            # type is ignored here as AuthLoginClient does not provide a signature for
            # oauth2_start_flow since it has different positional arguments between
            # NativeAppAuthClient and ConfidentialAppAuthClient
            self.login_client.oauth2_start_flow(  # type: ignore
                redirect_uri=redirect_uri,
                refresh_tokens=self.refresh_tokens,
                requested_scopes=auth_parameters.required_scopes,
            )

            # open authorize url in web-browser for user to authenticate
            url = self.login_client.oauth2_get_authorize_url(
                session_required_identities=auth_parameters.session_required_identities,
                session_required_single_domain=(
                    auth_parameters.session_required_single_domain
                ),
                session_required_policies=auth_parameters.session_required_policies,
                session_required_mfa=auth_parameters.session_required_mfa,
                prompt=auth_parameters.prompt,  # type: ignore
            )
            _open_webbrowser(url)

            # get auth code from server
            auth_code = server.wait_for_code()

        if isinstance(auth_code, BaseException):
            raise LocalServerError(
                f"Authorization failed with unexpected error:\n{auth_code}"
            )

        # get and return tokens
        return self.login_client.oauth2_exchange_code_for_tokens(auth_code)

    @contextmanager
    def start_local_server(self) -> t.Iterator[RedirectHTTPServer]:
        """
        Starts a RedirectHTTPServer in a thread as a context manager.
        """
        server = RedirectHTTPServer(
            server_address=self.server_address,
            handler_class=RedirectHandler,
            html_template=self.html_template,
        )
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

        yield server

        server.shutdown()
