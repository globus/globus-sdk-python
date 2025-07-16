import logging
from unittest import mock

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


def test_caller_info_takes_precedence_over_authorizer():
    transport = RequestsTransport()
    auth1 = mock.Mock()
    auth2 = mock.Mock()
    auth2.get_authorization_header.return_value = "Bearer token2"
    auth1.get_authorization_header.return_value = "Bearer token1"
    caller_info = RequestCallerInfo(authorizer=auth2)

    with mock.patch.object(transport, "session") as mock_session:
        mock_response = mock.Mock(status_code=200)
        mock_session.send.return_value = mock_response

        # Pass both parameters - caller_info should take precedence
        transport.request(
            "GET", "https://example.com", authorizer=auth1, caller_info=caller_info
        )

        # Verify that auth2 (from caller_info) was used, not auth1
        auth2.get_authorization_header.assert_called()
        auth1.get_authorization_header.assert_not_called()


def test_conflicting_authorizers_logs_warning(caplog):
    transport = RequestsTransport()
    auth1 = mock.Mock()
    auth2 = mock.Mock()
    auth2.get_authorization_header.return_value = "Bearer token2"
    auth1.get_authorization_header.return_value = "Bearer token1"
    caller_info = RequestCallerInfo(authorizer=auth2)

    with mock.patch.object(transport, "session") as mock_session:
        mock_response = mock.Mock(status_code=200)
        mock_session.send.return_value = mock_response

        with caplog.at_level(logging.WARNING):
            transport.request(
                "GET", "https://example.com", authorizer=auth1, caller_info=caller_info
            )

        # Verify warning was logged
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "WARNING"
        assert (
            "Both 'caller_info' and 'authorizer' parameters provided"
            in caplog.records[0].message
        )

        # Verify that auth2 (from caller_info) was used, not auth1
        auth2.get_authorization_header.assert_called()
        auth1.get_authorization_header.assert_not_called()


def test_same_authorizer_no_warning(caplog):
    transport = RequestsTransport()
    auth = mock.Mock()
    auth.get_authorization_header.return_value = "Bearer token"
    caller_info = RequestCallerInfo(authorizer=auth)

    with mock.patch.object(transport, "session") as mock_session:
        mock_response = mock.Mock(status_code=200)
        mock_session.send.return_value = mock_response

        with caplog.at_level(logging.WARNING):
            # Pass the same authorizer in both parameters - should not warn
            transport.request(
                "GET", "https://example.com", authorizer=auth, caller_info=caller_info
            )

        # Verify no warning was logged
        assert len(caplog.records) == 0

        # Verify that the authorizer was used
        auth.get_authorization_header.assert_called()
