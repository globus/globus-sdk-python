"""
Custom retry check collection for the TransferClient that overrides
the default check_transient_error
"""

from __future__ import annotations

from globus_sdk.transport import RetryCheck, RetryCheckResult, RetryContext
from globus_sdk.transport.default_retry_checks import (
    DEFAULT_RETRY_CHECKS,
    check_transient_error,
)


def check_transfer_transient_error(ctx: RetryContext) -> RetryCheckResult:
    """
    check for transient error status codes which could be resolved by
    retrying the request. Does not retry ExternalErrors or EndpointErrors
    as those are unlikely to actually be transient.

    :param ctx: The context object which describes the state of the request and the
        retries which may already have been attempted
    """
    retry_config = ctx.caller_info.retry_config
    if ctx.response is not None and (
        ctx.response.status_code in retry_config.transient_error_status_codes
    ):
        try:
            code = ctx.response.json()["code"]
        except (ValueError, KeyError):
            code = ""

        for non_retry_code in ("ExternalError", "EndpointError"):
            if non_retry_code in code:
                return RetryCheckResult.no_decision

        return RetryCheckResult.do_retry

    return RetryCheckResult.no_decision


# Transfer retry checks are the defaults with the transient error one replaced
TRANSFER_DEFAULT_RETRY_CHECKS: tuple[RetryCheck, ...] = tuple(
    check_transfer_transient_error if check is check_transient_error else check
    for check in DEFAULT_RETRY_CHECKS
)
