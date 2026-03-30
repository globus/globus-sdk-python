"""
Custom retry check collection for the TransferClientV2 that overrides
the default check_transient_error
"""

from __future__ import annotations

from globus_sdk.transport import RetryCheck, RetryCheckResult, RetryContext
from globus_sdk.transport.default_retry_checks import (
    DEFAULT_RETRY_CHECKS,
    check_transient_error,
)


def check_transfer_v2_transient_error(ctx: RetryContext) -> RetryCheckResult:
    """
    check for transient error status codes which could be resolved by
    retrying the request. Does not retry ExternalErrors or EndpointErrors
    as those are unlikely to actually be transient.

    :param ctx: The context object which describes the state of the request and the
        retries which may already have been attempted
    """
    # JSON:API uses "the most generally applicable HTTP error code" for the
    # status of the response, so if its a transient status code then all of the
    # error objects should also have transient status codes.
    retry_config = ctx.caller_info.retry_config
    if ctx.response is not None and (
        ctx.response.status_code in retry_config.transient_error_status_codes
    ):
        try:
            # if any of the error objects have a `code` of ExternalError or
            # EndpointError then the error likely isn't transient
            errors = ctx.response.json()["errors"]
            for error in errors:
                if error["code"] in ("ExternalError", "EndpointError"):
                    return RetryCheckResult.no_decision

        except (ValueError, KeyError):
            pass

        return RetryCheckResult.do_retry

    return RetryCheckResult.no_decision


# Transfer retry checks are the defaults with the transient error one replaced
TRANSFER_V2_DEFAULT_RETRY_CHECKS: tuple[RetryCheck, ...] = tuple(
    check_transfer_v2_transient_error if check is check_transient_error else check
    for check in DEFAULT_RETRY_CHECKS
)
