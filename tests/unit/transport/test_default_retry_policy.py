from unittest import mock

import pytest

from globus_sdk.transport import (
    DefaultRetryCheckCollection,
    RequestCallerInfo,
    RequestsTransport,
    RetryCheckResult,
    RetryCheckRunner,
    RetryConfiguration,
    RetryContext,
)


@pytest.mark.parametrize("http_status", (429, 503))
def test_retry_policy_respects_retry_after(mocksleep, http_status):
    retry_config = RetryConfiguration(checks=DefaultRetryCheckCollection())
    transport = RequestsTransport()
    checker = RetryCheckRunner(retry_config.checks)

    dummy_response = mock.Mock()
    dummy_response.headers = {"Retry-After": "5"}
    dummy_response.status_code = http_status
    caller_info = RequestCallerInfo(retry_configuration=retry_config)
    ctx = RetryContext(1, caller_info=caller_info, response=dummy_response)

    assert checker.should_retry(ctx) is True
    mocksleep.assert_not_called()
    transport._retry_sleep(retry_config, ctx)
    mocksleep.assert_called_once_with(5)


@pytest.mark.parametrize("http_status", (429, 503))
def test_retry_policy_ignores_retry_after_too_high(mocksleep, http_status):
    # set explicit max sleep to confirm that the value is capped here
    retry_config = RetryConfiguration(max_sleep=5, checks=DefaultRetryCheckCollection())
    transport = RequestsTransport()
    checker = RetryCheckRunner(retry_config.checks)

    dummy_response = mock.Mock()
    dummy_response.headers = {"Retry-After": "20"}
    dummy_response.status_code = http_status
    caller_info = RequestCallerInfo(retry_configuration=retry_config)
    ctx = RetryContext(1, caller_info=caller_info, response=dummy_response)

    assert checker.should_retry(ctx) is True
    mocksleep.assert_not_called()
    transport._retry_sleep(retry_config, ctx)
    mocksleep.assert_called_once_with(5)


@pytest.mark.parametrize("http_status", (429, 503))
def test_retry_policy_ignores_malformed_retry_after(mocksleep, http_status):
    retry_config = RetryConfiguration(checks=DefaultRetryCheckCollection())
    transport = RequestsTransport()
    checker = RetryCheckRunner(retry_config.checks)

    dummy_response = mock.Mock()
    dummy_response.headers = {"Retry-After": "not-an-integer"}
    dummy_response.status_code = http_status
    caller_info = RequestCallerInfo(retry_configuration=retry_config)
    ctx = RetryContext(1, caller_info=caller_info, response=dummy_response)

    assert checker.should_retry(ctx) is True
    mocksleep.assert_not_called()
    transport._retry_sleep(retry_config, ctx)
    mocksleep.assert_called_once()


@pytest.mark.parametrize(
    "checkname",
    [
        "check_retry_after_header",
        "check_transient_error",
    ],
)
def test_default_retry_check_noop_on_exception(checkname, mocksleep):
    retry_config = RetryConfiguration(checks=DefaultRetryCheckCollection())
    method = getattr(retry_config.checks, checkname)
    caller_info = RequestCallerInfo(retry_configuration=retry_config)
    ctx = RetryContext(1, caller_info=caller_info, exception=Exception("foo"))
    assert method(ctx) is RetryCheckResult.no_decision
