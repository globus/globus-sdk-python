"""
Custom retry check collection for the TransferClient that overrides
the default check_transient_error
"""

from globus_sdk.transport import (
    DefaultRetryCheckCollection,
    RetryCheckResult,
    RetryContext,
)


class TransferDefaultRetryCheckCollection(DefaultRetryCheckCollection):
    def check_transient_error(self, ctx: RetryContext) -> RetryCheckResult:
        """
        check for transient error status codes which could be resolved by
        retrying the request. Does not retry ExternalErrors or EndpointErrors
        as those are unlikely to actually be transient.

        :param ctx: The context object which describes the state of the request and the
            retries which may already have been attempted
        """
        if ctx.response is not None and (
            ctx.response.status_code in self.transient_error_status_codes
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
