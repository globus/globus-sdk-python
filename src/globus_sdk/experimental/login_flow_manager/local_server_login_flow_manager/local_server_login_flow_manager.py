from __future__ import annotations

import os
import threading
import typing as t
import webbrowser
from contextlib import contextmanager
from string import Template

from globus_sdk import AuthLoginClient, GlobusSDKUsageError, OAuthTokenResponse
from globus_sdk.experimental.auth_requirements_error import (
    GlobusAuthorizationParameters,
)
from globus_sdk.experimental.login_flow_manager.login_flow_manager import (
    LoginFlowManager,
)

from ._local_server import (
    DEFAULT_HTML_TEMPLATE,
    LocalServerError,
    RedirectHandler,
    RedirectHTTPServer,
)

if t.TYPE_CHECKING:
    from globus_sdk.experimental.globus_app import GlobusAppConfig

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
        if hasattr(browser, "name"):
            browser_name = browser.name
        elif hasattr(browser, "_name"):
            # MacOSXOSAScript only supports a public name attribute in py311 and later.
            # https://github.com/python/cpython/issues/82828
            browser_name = browser._name
        else:
            raise LocalServerLoginFlowError("Unable to determine local browser name.")

        if browser_name in BROWSER_BLACKLIST:
            raise LocalServerLoginFlowError(
                "Cannot use LocalServerLoginFlowManager with "
                f"text-only browser '{browser_name}'"
            )

        if not browser.open(url, new=1):
            raise LocalServerLoginFlowError(f"Failed to open browser '{browser_name}'")
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
        request_refresh_tokens: bool = False,
        native_prefill_named_grant: str | None = None,
        server_address: tuple[str, int] = ("127.0.0.1", 0),
        html_template: Template = DEFAULT_HTML_TEMPLATE,
    ):
        """
        :param login_client: The ``AuthLoginClient`` that will be making the Globus
            Auth API calls needed for the authentication flow. Note that this
            must either be a NativeAppAuthClient or a templated
            ConfidentialAppAuthClient, standard ConfidentialAppAuthClients cannot
            use the web auth-code flow.
        :param request_refresh_tokens: Control whether refresh tokens will be requested.
        :param native_prefill_named_grant: The named grant label to prefill on the
            consent page when using a NativeAppAuthClient.
        :param html_template: Optional HTML Template to be populated with the values
            login_result and post_login_message and displayed to the user.
        :param server_address: Optional tuple of the form (host, port) to specify an
            address to run the local server at.
        """
        super().__init__(
            login_client,
            request_refresh_tokens=request_refresh_tokens,
            native_prefill_named_grant=native_prefill_named_grant,
        )
        self.server_address = server_address
        self.html_template = html_template

    @classmethod
    def for_globus_app(
        cls, app_name: str, login_client: AuthLoginClient, config: GlobusAppConfig
    ) -> LocalServerLoginFlowManager:
        """
        Create a ``LocalServerLoginFlowManager`` for a given ``GlobusAppConfig``.

        :param app_name: The name of the app to use for prefilling the named grant,.
        :param login_client: The ``AuthLoginClient`` to use to drive Globus Auth flows.
        :param config: A ``GlobusAppConfig`` to configure the login flow.
        :returns: A ``LocalServerLoginFlowManager`` instance.
        :raises: GlobusSDKUsageError if a custom login_redirect_uri is defined in
            the config.
        """
        if config.login_redirect_uri:
            # A "local server" relies on the user being redirected back to the server
            # running on the local machine, so it can't use a custom redirect URI.
            msg = "Cannot define a custom redirect_uri for LocalServerLoginFlowManager."
            raise GlobusSDKUsageError(msg)

        return cls(
            login_client,
            request_refresh_tokens=config.request_refresh_tokens,
            native_prefill_named_grant=app_name,
        )

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
            raise LocalServerError(msg)

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
