"""
Classes used by the LocalServerLoginFlowManager to automatically receive an
auth code from a redirect after user authentication through a locally run web-server.

These classes generally shouldn't need to be used directly.
"""

from __future__ import annotations

import os
import queue
import socket
import sys
import time
import typing as t
from http.server import BaseHTTPRequestHandler, HTTPServer
from string import Template
from urllib.parse import parse_qsl, urlparse

if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:  # Python < 3.9
    import importlib_resources

from globus_sdk.experimental import html_files

_IS_WINDOWS = os.name == "nt"

DEFAULT_HTML_TEMPLATE = Template(
    importlib_resources.files(html_files)
    .joinpath("local_server_landing_page.html")
    .read_text()
)


class LocalServerError(Exception):
    """
    Error class for errors raised by the local server when using a
    LocalServerLoginFlowManager
    """


class RedirectHTTPServer(HTTPServer):
    """
    HTTPServer that accepts an html_template to be displayed to the user
    and uses a Queue to receive an auth_code from its RequestHandler.
    """

    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[BaseHTTPRequestHandler],
        html_template: Template,
    ) -> None:
        super().__init__(server_address, handler_class)

        self.html_template = html_template
        self._auth_code_queue: queue.Queue[str | BaseException] = queue.Queue()

    def handle_error(
        self,
        request: socket.socket | tuple[bytes, socket.socket],
        client_address: t.Any,
    ) -> None:
        _, excval, _ = sys.exc_info()
        assert excval is not None
        self._auth_code_queue.put(excval)

    def return_code(self, code: str | BaseException) -> None:
        self._auth_code_queue.put_nowait(code)

    def wait_for_code(self) -> str | BaseException:
        # Windows needs special handling as blocking prevents ctrl-c interrupts
        if _IS_WINDOWS:
            deadline = time.time() + 3600
            while time.time() < deadline:
                try:
                    return self._auth_code_queue.get()
                except queue.Empty:
                    time.sleep(1)
        else:
            try:
                return self._auth_code_queue.get(block=True, timeout=3600)
            except queue.Empty:
                pass
        raise LocalServerError("Login timed out. Please try again.")


class RedirectHandler(BaseHTTPRequestHandler):
    """
    BaseHTTPRequestHandler to be used by RedirectHTTPServer.
    Displays the RedirectHTTPServer's html_template and parses auth_code out of
    the redirect url.
    """

    server: RedirectHTTPServer

    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html_template = self.server.html_template
        query_params = dict(parse_qsl(urlparse(self.path).query))
        code = query_params.get("code")
        if code:
            self.wfile.write(
                html_template.substitute(
                    post_login_message="", login_result="Login successful"
                ).encode("utf-8")
            )
            self.server.return_code(code)
        else:
            msg = query_params.get("error_description", query_params.get("error"))

            self.wfile.write(
                html_template.substitute(
                    post_login_message=msg, login_result="Login failed"
                ).encode("utf-8")
            )

            self.server.return_code(LocalServerError(msg))
