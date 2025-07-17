from unittest import mock

from globus_sdk.transport import (
    RequestCallerInfo,
    RetryCheckResult,
    RetryCheckRunner,
    RetryContext,
)


def _make_test_retry_context(*, status=200, exception=None, response=None):
    caller_info = RequestCallerInfo(authorizer=None)
    if exception:
        return RetryContext(1, caller_info=caller_info, exception=exception)
    elif response:
        return RetryContext(1, caller_info=caller_info, response=response)

    dummy_response = mock.Mock()
    dummy_response.status_code = 200
    return RetryContext(1, caller_info=caller_info, response=dummy_response)


def test_retry_check_runner_should_retry_explicit_on_first_check():
    def check1(ctx):
        return RetryCheckResult.do_not_retry

    def check2(ctx):
        return RetryCheckResult.do_retry

    failing_checker = RetryCheckRunner([check1, check2])
    assert failing_checker.should_retry(_make_test_retry_context()) is False
    passing_checker = RetryCheckRunner([check2, check1])
    assert passing_checker.should_retry(_make_test_retry_context()) is True


def test_retry_check_runner_fallthrough_to_false():
    def check1(ctx):
        return RetryCheckResult.no_decision

    def check2(ctx):
        return RetryCheckResult.no_decision

    checker = RetryCheckRunner([check1, check2])
    assert checker.should_retry(_make_test_retry_context()) is False
