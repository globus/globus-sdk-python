from unittest.mock import Mock

import pytest

from globus_sdk.experimental.login_flow_manager._local_server import (
    DEFAULT_HTML_TEMPLATE,
    LocalServerError,
    RedirectHandler,
    RedirectHTTPServer,
)


@pytest.mark.parametrize(
    "url,expected_result",
    [
        (b"localhost?code=abc123", "abc123"),
        (b"localhost?error=bad_login", LocalServerError("bad_login")),
        (b"localhost", LocalServerError(None)),
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
    elif isinstance(result, LocalServerError):
        assert result.args == expected_result.args
    else:
        raise AssertionError("unexpected result type")
