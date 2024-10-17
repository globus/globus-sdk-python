from __future__ import annotations

import os
import threading
import typing as t
import webbrowser
from contextlib import contextmanager
from string import Template

import globus_sdk
from globus_sdk.gare import GlobusAuthorizationParameters
from globus_sdk.login_flows.login_flow_manager import LoginFlowManager
from globus_sdk.utils import get_nice_hostname

from .errors import LocalServerEnvironmentalLoginError, LocalServerLoginError
from .local_server import DEFAULT_HTML_TEMPLATE, RedirectHandler, RedirectHTTPServer

if t.TYPE_CHECKING:
    from globus_sdk.globus_app import GlobusAppConfig

# a list of text-only browsers which are not allowed for use because they don't work
# with Globus Auth login flows and seize control of the terminal
#
# see the webbrowser library for a list of names:
#   https://github.com/python/cpython/blob/69cdeeb93e0830004a495ed854022425b93b3f3e/Lib/webbrowser.py#L489-L502
BROWSER_DENY_LIST = ["lynx", "www-browser", "links", "elinks", "w3m"]


def _check_remote_session() -> None:
    """
    Try to check if this is being run during a remote session, if so
    raise LocalServerLoginFlowError
    """
    if bool(os.environ.get("SSH_TTY", os.environ.get("SSH_CONNECTION"))):
        raise LocalServerEnvironmentalLoginError(
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
        if hasattr(browser, "name"):
            browser_name = browser.name
        elif hasattr(browser, "_name"):
            # MacOSXOSAScript only supports a public name attribute in py311 and later.
            # https://github.com/python/cpython/issues/82828
            browser_name = browser._name
        else:
            raise LocalServerEnvironmentalLoginError(
                "Unable to determine local browser name."
            )

        if browser_name in BROWSER_DENY_LIST:
            raise LocalServerEnvironmentalLoginError(
                "Cannot use LocalServerLoginFlowManager with "
                f"text-only browser '{browser_name}'"
            )

        if not browser.open(url, new=1):
            raise LocalServerEnvironmentalLoginError(
                f"Failed to open browser '{browser_name}'"
            )
    except webbrowser.Error as exc:
        raise LocalServerEnvironmentalLoginError("Failed to open browser") from exc


class LocalServerLoginFlowManager(LoginFlowManager):
    """
    A login flow manager which uses a locally hosted server to drive authentication-code
    token grants. The local server is used as the authorization redirect URI,
    automatically receiving the auth code from Globus Auth after authentication/consent.

    :param AuthLoginClient login_client: The client that will be making Globus
        Auth API calls required for a login flow.
    :param bool request_refresh_tokens: A signal of whether refresh tokens are expected
        to be requested, in addition to access tokens.
    :param str native_prefill_named_grant: A string to prefill in a Native App login
        flow. This value is only used if the `login_client` is a native client.
    :param Template html_template: Optional HTML Template to be populated with the
        values login_result and post_login_message and displayed to the user. A simple
        default is supplied if not provided which informs the user that the login was
        successful and that they may close the browser window.
    :param tuple[str, int] server_address: Optional tuple of the form (host, port) to
        specify an address to run the local server at. Defaults to ("127.0.0.1", 0).
    """

    def __init__(
        self,
        login_client: globus_sdk.AuthLoginClient,
        *,
        request_refresh_tokens: bool = False,
        native_prefill_named_grant: str | None = None,
        server_address: tuple[str, int] = ("localhost", 0),
        html_template: Template = DEFAULT_HTML_TEMPLATE,
    ) -> None:
        super().__init__(
            login_client,
            request_refresh_tokens=request_refresh_tokens,
            native_prefill_named_grant=native_prefill_named_grant,
        )
        self.server_address = server_address
        self.html_template = html_template

    @classmethod
    def for_globus_app(
        cls,
        app_name: str,
        login_client: globus_sdk.AuthLoginClient,
        config: GlobusAppConfig,
    ) -> LocalServerLoginFlowManager:
        """
        Create a ``LocalServerLoginFlowManager`` for use in a GlobusApp.

        :param app_name: The name of the app. Will be prefilled in native auth flows.
        :param login_client: A client used to make Globus Auth API calls.
        :param config: A GlobusApp-bounded object used to configure login flow manager.
        :raises GlobusSDKUsageError: if app config is incompatible with the manager.
        """
        if config.login_redirect_uri:
            # A "local server" relies on the user being redirected back to the server
            # running on the local machine, so it can't use a custom redirect URI.
            msg = "Cannot define a custom redirect_uri for LocalServerLoginFlowManager."
            raise globus_sdk.GlobusSDKUsageError(msg)
        if not isinstance(login_client, globus_sdk.NativeAppAuthClient):
            # Globus Auth has special provisions for native clients which allow implicit
            # redirect url grant to localhost:<any-port>. This is required for the
            # LocalServerLoginFlowManager to work and is not reproducible in
            # confidential clients.
            msg = "LocalServerLoginFlowManager is only supported for Native Apps."
            raise globus_sdk.GlobusSDKUsageError(msg)

        hostname = get_nice_hostname()
        if hostname:
            prefill = f"{app_name} on {hostname}"
        else:
            prefill = app_name

        return cls(
            login_client,
            request_refresh_tokens=config.request_refresh_tokens,
            native_prefill_named_grant=prefill,
        )

    def run_login_flow(
        self,
        auth_parameters: GlobusAuthorizationParameters,
    ) -> globus_sdk.OAuthTokenResponse:
        """
        Run an interactive login flow using a locally hosted server to get tokens
        for the user.

        :param auth_parameters: ``GlobusAuthorizationParameters`` passed through
            to the authentication flow to control how the user will authenticate.
        :raises LocalServerEnvironmentalLoginError: If the local server login flow
            cannot be run due to known failure conditions such as remote sessions or
            text-only browsers.
        :raises LocalServerLoginError: If the local server login flow fails for any
            reason.
        """
        _check_remote_session()

        with self.background_local_server() as server:
            host, port = server.socket.getsockname()
            redirect_uri = f"http://{host}:{port}"

            # open authorize url in web-browser for user to authenticate
            authorize_url = self._get_authorize_url(auth_parameters, redirect_uri)
            _open_webbrowser(authorize_url)

            # get auth code from server
            auth_code = server.wait_for_code()

        if isinstance(auth_code, BaseException):
            msg = f"Authorization failed with unexpected error:\n{auth_code}."
            raise LocalServerLoginError(msg)

        # get and return tokens
        return self.login_client.oauth2_exchange_code_for_tokens(auth_code)

    @contextmanager
    def background_local_server(self) -> t.Iterator[RedirectHTTPServer]:
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
