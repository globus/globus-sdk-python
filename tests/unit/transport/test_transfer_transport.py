from unittest import mock

from globus_sdk.services.transfer.transport import TRANSFER_DEFAULT_RETRY_CHECKS
from globus_sdk.transport import (
    RequestCallerInfo,
    RetryCheckCollection,
    RetryCheckRunner,
    RetryConfig,
    RetryContext,
)
from globus_sdk.transport.default_retry_checks import DEFAULT_RETRY_CHECKS


def test_transfer_only_replaces_checks():
    # their length matches, meaning things line up
    assert len(TRANSFER_DEFAULT_RETRY_CHECKS) == len(DEFAULT_RETRY_CHECKS)

    # also confirm that this holds once loaded
    # if the implementation of the RetryCheckCollection becomes sensitive to
    # the contents of these tuples, this could fail
    default_variant = RetryCheckCollection()
    default_variant.register_many_checks(DEFAULT_RETRY_CHECKS)

    transfer_variant = RetryCheckCollection()
    transfer_variant.register_many_checks(TRANSFER_DEFAULT_RETRY_CHECKS)

    assert len(default_variant) == len(transfer_variant)


def test_transfer_does_not_retry_external():
    retry_config = RetryConfig()
    retry_config.checks.register_many_checks(TRANSFER_DEFAULT_RETRY_CHECKS)
    checker = RetryCheckRunner(retry_config.checks)

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
    caller_info = RequestCallerInfo(retry_config=retry_config)
    ctx = RetryContext(1, caller_info=caller_info, response=dummy_response)

    assert checker.should_retry(ctx) is False


def test_transfer_does_not_retry_endpoint_error():
    retry_config = RetryConfig()
    retry_config.checks.register_many_checks(TRANSFER_DEFAULT_RETRY_CHECKS)
    checker = RetryCheckRunner(retry_config.checks)

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
    caller_info = RequestCallerInfo(retry_config=retry_config)
    ctx = RetryContext(1, caller_info=caller_info, response=dummy_response)

    assert checker.should_retry(ctx) is False


def test_transfer_retries_others():
    retry_config = RetryConfig()
    retry_config.checks.register_many_checks(TRANSFER_DEFAULT_RETRY_CHECKS)
    checker = RetryCheckRunner(retry_config.checks)

    def _raise_value_error():
        raise ValueError()

    dummy_response = mock.Mock()
    dummy_response.json = _raise_value_error
    dummy_response.status_code = 502
    caller_info = RequestCallerInfo(retry_config=retry_config)
    ctx = RetryContext(1, caller_info=caller_info, response=dummy_response)

    assert checker.should_retry(ctx) is True
