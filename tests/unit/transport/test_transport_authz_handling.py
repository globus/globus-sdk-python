from unittest import mock

import pytest

from globus_sdk.authorizers import NullAuthorizer
from globus_sdk.transport import RequestCallerInfo, RequestsTransport


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


def test_request_caller_info_creation():
    mock_authorizer = mock.Mock()
    caller_info = RequestCallerInfo(authorizer=mock_authorizer)

    assert caller_info.authorizer is mock_authorizer


def test_requests_transport_accepts_caller_info():
    transport = RequestsTransport()
    mock_authorizer = mock.Mock()
    mock_authorizer.get_authorization_header.return_value = "Bearer token"
    caller_info = RequestCallerInfo(authorizer=mock_authorizer)

    with mock.patch.object(transport, "session") as mock_session:
        mock_response = mock.Mock(status_code=200)
        mock_session.send.return_value = mock_response

        response = transport.request(
            "GET", "https://example.com", caller_info=caller_info
        )

        assert response.status_code == 200


def test_requests_transport_caller_info_required():
    transport = RequestsTransport()

    with pytest.raises(TypeError):
        transport.request("GET", "https://example.com")


def test_requests_transport_keyword_only():
    transport = RequestsTransport()
    caller_info = RequestCallerInfo(authorizer=None)

    with pytest.raises(TypeError):
        transport.request("GET", "https://example.com", caller_info)


def test_request_caller_info_with_none_authorizer():
    caller_info = RequestCallerInfo(authorizer=None)
    assert caller_info.authorizer is None
