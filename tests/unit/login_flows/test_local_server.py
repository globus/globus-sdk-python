from unittest.mock import Mock

import pytest

from globus_sdk.login_flows import LocalServerLoginError
from globus_sdk.login_flows.local_server_login_flow_manager.local_server import (  # noqa: E501
    DEFAULT_HTML_TEMPLATE,
    RedirectHandler,
    RedirectHTTPServer,
)


def test_default_html_template_contains_expected_text():
    # basic integrity test
    assert "<h1>Globus Login Result</h1>" in DEFAULT_HTML_TEMPLATE.substitute(
        post_login_message="", login_result="Login successful"
    )


@pytest.mark.parametrize(
    "url,expected_result",
    [
        (b"localhost?code=abc123", "abc123"),
        (b"localhost?error=bad_login", LocalServerLoginError("bad_login")),
        (b"localhost", LocalServerLoginError(None)),
    ],
)
def test_server(url, expected_result):
    """
    Setup a RedirectHTTPServer and pass it mocked HTTP GET requests to have
    its RedirectHandler handle
    """
    server = RedirectHTTPServer(
        server_address=("", 0),
        handler_class=RedirectHandler,
        html_template=DEFAULT_HTML_TEMPLATE,
    )

    # setup Mocks to look like a connection to a file for reading the HTTP data
    mock_file = Mock()
    mock_file.readline.side_effect = [
        b"GET " + url + b" HTTP/1.1",
        b"Host: localhost",
        b"",
    ]
    mock_conn = Mock()
    mock_conn.makefile.return_value = mock_file

    # handle the request, then cleanup
    server.finish_request(mock_conn, ("", 0))
    server.server_close()

    # confirm expected results
    result = server.wait_for_code()
    if isinstance(result, str):
        assert result == expected_result
    elif isinstance(result, LocalServerLoginError):
        assert result.args == expected_result.args
    else:
        raise AssertionError("unexpected result type")
