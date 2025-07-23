from unittest import mock

import pytest

from globus_sdk.authorizers import NullAuthorizer
from globus_sdk.transport import RequestCallerInfo, RequestsTransport, RetryConfig


def test_will_not_modify_authz_header_without_authorizer():
    request = mock.Mock()
    request.headers = {}

    transport = RequestsTransport()
    transport._set_authz_header(None, request)
    assert request.headers == {}

    request.headers["Authorization"] = "foo bar"
    transport._set_authz_header(None, request)
    assert request.headers == {"Authorization": "foo bar"}


def test_will_null_authz_header_with_null_authorizer():
    request = mock.Mock()
    request.headers = {}

    transport = RequestsTransport()
    transport._set_authz_header(NullAuthorizer(), request)
    assert request.headers == {}

    request.headers["Authorization"] = "foo bar"
    transport._set_authz_header(NullAuthorizer(), request)
    assert request.headers == {}


def test_requests_transport_accepts_caller_info():
    retry_config = RetryConfig()
    transport = RequestsTransport()
    mock_authorizer = mock.Mock()
    mock_authorizer.get_authorization_header.return_value = "Bearer token"
    caller_info = RequestCallerInfo(
        retry_config=retry_config, authorizer=mock_authorizer
    )

    with mock.patch.object(transport, "session") as mock_session:
        mock_response = mock.Mock(status_code=200)
        mock_session.send.return_value = mock_response

        response = transport.request(
            "GET", "https://example.com", caller_info=caller_info
        )

        assert response.status_code == 200

        sent_request = mock_session.send.call_args[0][0]
        assert sent_request.headers["Authorization"] == "Bearer token"


def test_requests_transport_caller_info_required():
    transport = RequestsTransport()

    with pytest.raises(TypeError):
        transport.request("GET", "https://example.com")


def test_requests_transport_keyword_only():
    retry_config = RetryConfig()
    transport = RequestsTransport()
    caller_info = RequestCallerInfo(retry_config=retry_config)

    with pytest.raises(TypeError):
        transport.request("GET", "https://example.com", caller_info)
