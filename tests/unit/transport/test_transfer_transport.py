from unittest import mock

from globus_sdk.services.transfer.transport import TransferRequestsTransport
from globus_sdk.transport import RetryCheckRunner, RetryContext


def test_transfer_does_not_retry_external():
    transport = TransferRequestsTransport()
    checker = RetryCheckRunner(transport.retry_checks)

    body = {
        "HTTP status": "502",
        "code": "ExternalError.DirListingFailed.GCDisconnected",
        "error_name": "Transfer API Error",
        "message": "The GCP endpoint is not currently connected to Globus",
        "request_id": "rhvcR0aHX",
    }

    dummy_response = mock.Mock()
    dummy_response.json = lambda: body
    dummy_response.status_code = 502
    ctx = RetryContext(1, response=dummy_response)

    assert checker.should_retry(ctx) is False


def test_transfer_does_not_retry_endpoint_error():
    transport = TransferRequestsTransport()
    checker = RetryCheckRunner(transport.retry_checks)

    body = {
        "HTTP status": "502",
        "code": "EndpointError",
        "error_name": "Transfer API Error",
        "message": (
            "This GCSv5 is older than version 5.4.62 and does not support local user "
            "selection"
        ),
        "request_id": "istNh0Zpz",
    }

    dummy_response = mock.Mock()
    dummy_response.json = lambda: body
    dummy_response.status_code = 502
    ctx = RetryContext(1, response=dummy_response)

    assert checker.should_retry(ctx) is False


def test_transfer_retries_others():
    transport = TransferRequestsTransport()
    checker = RetryCheckRunner(transport.retry_checks)

    def _raise_value_error():
        raise ValueError()

    dummy_response = mock.Mock()
    dummy_response.json = _raise_value_error
    dummy_response.status_code = 502
    ctx = RetryContext(1, response=dummy_response)

    assert checker.should_retry(ctx) is True
