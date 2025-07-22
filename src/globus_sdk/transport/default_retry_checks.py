from __future__ import annotations

import requests

from .retry import (
    RetryCheck,
    RetryCheckFlags,
    RetryCheckResult,
    RetryContext,
    set_retry_check_flags,
)


def check_request_exception(ctx: RetryContext) -> RetryCheckResult:
    """
    Check if a network error was encountered

    :param ctx: The context object which describes the state of the request and the
        retries which may already have been attempted.
    """
    if ctx.exception and isinstance(ctx.exception, requests.RequestException):
        return RetryCheckResult.do_retry
    return RetryCheckResult.no_decision


def check_retry_after_header(ctx: RetryContext) -> RetryCheckResult:
    """
    Check for a retry-after header if the response had a matching status

    :param ctx: The context object which describes the state of the request and the
        retries which may already have been attempted.
    """
    retry_config = ctx.caller_info.retry_config
    if ctx.response is None or (
        ctx.response.status_code not in retry_config.retry_after_status_codes
    ):
        return RetryCheckResult.no_decision
    retry_after = _parse_retry_after(ctx.response)
    if retry_after:
        ctx.backoff = float(retry_after)
    return RetryCheckResult.do_retry


def check_transient_error(ctx: RetryContext) -> RetryCheckResult:
    """
    Check for transient error status codes which could be resolved by retrying
    the request

    :param ctx: The context object which describes the state of the request and the
        retries which may already have been attempted.
    """
    retry_config = ctx.caller_info.retry_config
    if ctx.response is not None and (
        ctx.response.status_code in retry_config.transient_error_status_codes
    ):
        return RetryCheckResult.do_retry
    return RetryCheckResult.no_decision


@set_retry_check_flags(RetryCheckFlags.RUN_ONCE)
def check_expired_authorization(ctx: RetryContext) -> RetryCheckResult:
    """
    This check evaluates whether or not there is invalid or expired authorization
    information which could be updated with some action -- most typically a token
    refresh for an expired access token.

    The check is flagged to only run once per request.

    :param ctx: The context object which describes the state of the request and the
        retries which may already have been attempted.
    """
    retry_config = ctx.caller_info.retry_config
    if (  # is the current check applicable?
        ctx.response is None
        or ctx.caller_info is None
        or ctx.caller_info.authorizer is None
        or (
            ctx.response.status_code
            not in retry_config.expired_authorization_status_codes
        )
    ):
        return RetryCheckResult.no_decision

    # run the authorizer's handler, and 'do_retry' if the handler indicated
    # that it was able to make a change which should make the request retryable
    if ctx.caller_info.authorizer.handle_missing_authorization():
        return RetryCheckResult.do_retry
    return RetryCheckResult.no_decision


def _parse_retry_after(response: requests.Response) -> int | None:
    """
    Get the 'Retry-After' header as an int.

    :param response: The response to parse.
    """
    val = response.headers.get("Retry-After")
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None


DEFAULT_RETRY_CHECKS: tuple[RetryCheck, ...] = (
    check_expired_authorization,
    check_request_exception,
    check_retry_after_header,
    check_transient_error,
)
