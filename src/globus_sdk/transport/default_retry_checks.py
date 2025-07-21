from __future__ import annotations

import requests

from .retry import (
    RetryCheckCollection,
    RetryCheckFlags,
    RetryCheckResult,
    RetryContext,
    set_retry_check_flags,
)


class DefaultRetryCheckCollection(RetryCheckCollection):
    """The default checks for the SDK.

    :param retry_after_status_codes: status codes for responses which may have
        a Retry-After header
    :param transient_error_status_codes: status codes for error responses which
        should generally be retried
    :param expired_authorization_status_codes: status codes indicating that
        authorization info was missing or expired
    """

    def __init__(
        self,
        *,
        retry_after_status_codes: tuple[int, ...] = (429, 503),
        transient_error_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504),
        expired_authorization_status_codes: tuple[int, ...] = (401,),
    ) -> None:
        super().__init__()

        self.retry_after_status_codes = retry_after_status_codes
        self.transient_error_status_codes = transient_error_status_codes
        self.expired_authorization_status_codes = expired_authorization_status_codes

        self.register_check(self.check_expired_authorization)
        self.register_check(self.check_request_exception)
        self.register_check(self.check_retry_after_header)
        self.register_check(self.check_transient_error)

    def check_request_exception(self, ctx: RetryContext) -> RetryCheckResult:
        """
        Check if a network error was encountered

        :param ctx: The context object which describes the state of the request and the
            retries which may already have been attempted.
        """
        if ctx.exception and isinstance(ctx.exception, requests.RequestException):
            return RetryCheckResult.do_retry
        return RetryCheckResult.no_decision

    def check_retry_after_header(self, ctx: RetryContext) -> RetryCheckResult:
        """
        Check for a retry-after header if the response had a matching status

        :param ctx: The context object which describes the state of the request and the
            retries which may already have been attempted.
        """
        if (
            ctx.response is None
            or ctx.response.status_code not in self.retry_after_status_codes
        ):
            return RetryCheckResult.no_decision
        retry_after = self.parse_retry_after(ctx.response)
        if retry_after:
            ctx.backoff = float(retry_after)
        return RetryCheckResult.do_retry

    def check_transient_error(self, ctx: RetryContext) -> RetryCheckResult:
        """
        Check for transient error status codes which could be resolved by retrying
        the request

        :param ctx: The context object which describes the state of the request and the
            retries which may already have been attempted.
        """
        if ctx.response is not None and (
            ctx.response.status_code in self.transient_error_status_codes
        ):
            return RetryCheckResult.do_retry
        return RetryCheckResult.no_decision

    @set_retry_check_flags(RetryCheckFlags.RUN_ONCE)
    def check_expired_authorization(self, ctx: RetryContext) -> RetryCheckResult:
        """
        This check evaluates whether or not there is invalid or expired authorization
        information which could be updated with some action -- most typically a token
        refresh for an expired access token.

        The check is flagged to only run once per request.

        :param ctx: The context object which describes the state of the request and the
            retries which may already have been attempted.
        """
        if (  # is the current check applicable?
            ctx.response is None
            or ctx.caller_info is None
            or ctx.caller_info.authorizer is None
            or ctx.response.status_code not in self.expired_authorization_status_codes
        ):
            return RetryCheckResult.no_decision

        # run the authorizer's handler, and 'do_retry' if the handler indicated
        # that it was able to make a change which should make the request retryable
        if ctx.caller_info.authorizer.handle_missing_authorization():
            return RetryCheckResult.do_retry
        return RetryCheckResult.no_decision

    def parse_retry_after(self, response: requests.Response) -> int | None:
        """Get the 'Retry-After' header as an int."""
        val = response.headers.get("Retry-After")
        if not val:
            return None
        try:
            return int(val)
        except ValueError:
            return None
