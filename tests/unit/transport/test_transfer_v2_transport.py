from unittest import mock

import pytest

from globus_sdk.experimental.transfer_v2.transport import (
    TRANSFER_V2_DEFAULT_RETRY_CHECKS,
)
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
    assert len(TRANSFER_V2_DEFAULT_RETRY_CHECKS) == len(DEFAULT_RETRY_CHECKS)

    # also confirm that this holds once loaded
    # if the implementation of the RetryCheckCollection becomes sensitive to
    # the contents of these tuples, this could fail
    default_variant = RetryCheckCollection()
    default_variant.register_many_checks(DEFAULT_RETRY_CHECKS)

    transfer_variant = RetryCheckCollection()
    transfer_variant.register_many_checks(TRANSFER_V2_DEFAULT_RETRY_CHECKS)

    assert len(default_variant) == len(transfer_variant)


@pytest.mark.parametrize(
    "body,status_code,expected_should_retry",
    [
        # single ExternalError should not retry
        (
            {
                "errors": [
                    {
                        "status": 502,
                        "code": "ExternalError",
                        "detail": (
                            "The GCP endpoint is not currently connected to Globus"
                        ),
                    }
                ],
                "meta": {
                    "request_id": "rhvcR0aHX",
                },
            },
            502,
            False,
        ),
        # single EndpointError should not retry
        (
            {
                "errors": [
                    {
                        "status": 502,
                        "code": "EndpointError",
                        "detail": (
                            "This GCSv5 is older than version 5.4.62 and does "
                            "not support local user selection"
                        ),
                    }
                ],
                "meta": {
                    "request_id": "istNh0Zpz",
                },
            },
            502,
            False,
        ),
        # other 502 should retry
        (
            {
                "errors": [
                    {
                        "status": 502,
                        "code": "BadGateway",
                        "detail": "Something went wrong with the proxy server",
                    }
                ],
                "meta": {
                    "request_id": "istNh0Zpz",
                },
            },
            502,
            True,
        ),
        # sandwiched ExternalError should not retry
        (
            {
                "errors": [
                    {
                        "status": 500,
                        "code": "InternalError",
                        "detail": "An internal processing error has occurred",
                    },
                    {
                        "status": 502,
                        "code": "ExternalError",
                        "detail": (
                            "The GCP endpoint is not currently connected to Globus"
                        ),
                    },
                    {
                        "status": 502,
                        "code": "BadGateway",
                        "detail": "Something went wrong with the proxy server",
                    },
                ],
                "meta": {
                    "request_id": "istNh0Zpz",
                },
            },
            500,
            False,
        ),
        # multiple 500s should retry
        (
            {
                "errors": [
                    {
                        "status": 500,
                        "code": "InternalError",
                        "detail": "An internal processing error has occurred",
                    },
                    {
                        "status": 502,
                        "code": "BadGateway",
                        "detail": "Something went wrong with the proxy server",
                    },
                ],
                "meta": {
                    "request_id": "istNh0Zpz",
                },
            },
            500,
            True,
        ),
    ],
)
def test_transfer_v2_default_retry_checks(body, status_code, expected_should_retry):
    retry_config = RetryConfig()
    retry_config.checks.register_many_checks(TRANSFER_V2_DEFAULT_RETRY_CHECKS)
    checker = RetryCheckRunner(retry_config.checks)

    dummy_response = mock.Mock()
    dummy_response.json = lambda: body
    dummy_response.status_code = status_code
    caller_info = RequestCallerInfo(retry_config=retry_config)
    ctx = RetryContext(1, caller_info=caller_info, response=dummy_response)

    assert checker.should_retry(ctx) is expected_should_retry


def test_transfer_v2_default_retry_checks_value_error():
    retry_config = RetryConfig()
    retry_config.checks.register_many_checks(TRANSFER_V2_DEFAULT_RETRY_CHECKS)
    checker = RetryCheckRunner(retry_config.checks)

    # simulate the error not having valid json
    def _raise_value_error():
        raise ValueError()

    dummy_response = mock.Mock()
    dummy_response.json = _raise_value_error
    dummy_response.status_code = 502
    caller_info = RequestCallerInfo(retry_config=retry_config)
    ctx = RetryContext(1, caller_info=caller_info, response=dummy_response)

    assert checker.should_retry(ctx) is True
