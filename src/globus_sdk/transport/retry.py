from __future__ import annotations

import enum
import logging
import typing as t

import requests

from globus_sdk.authorizers import GlobusAuthorizer

log = logging.getLogger(__name__)

C = t.TypeVar("C", bound=t.Callable[..., t.Any])


class RetryContext:
    """
    The RetryContext is an object passed to retry checks in order to determine whether
    or not a request should be retried. The context is constructed after each request,
    regardless of success or failure.

    If an exception was raised, the context will contain that exception object.
    Otherwise, the context will contain a response object. Exactly one of ``response``
    or ``exception`` will be present.

    :param attempt: The request attempt number, starting at 0.
    :type attempt: int
    :param response: The response on a successful request
    :type response: requests.Response
    :param exception: The error raised when trying to send the request
    :type exception: Exception
    :param authorizer: The authorizer object from the client making the request
    :type authorizer: :class:`GlobusAuthorizer \
        <globus_sdk.authorizers.GlobusAuthorizer>`
    """

    def __init__(
        self,
        attempt: int,
        *,
        authorizer: GlobusAuthorizer | None = None,
        response: requests.Response | None = None,
        exception: Exception | None = None,
    ):
        # retry attempt number
        self.attempt = attempt
        # if there is an authorizer for the request, it will be available in the context
        self.authorizer = authorizer
        # the response or exception from a request
        # we expect exactly one of these to be non-null
        self.response = response
        self.exception = exception
        # the retry delay or "backoff" before retrying
        self.backoff: float | None = None


class RetryCheckResult(enum.Enum):
    #: yes, retry the request
    do_retry = enum.auto()
    #: no, do not retry the request
    do_not_retry = enum.auto()
    #: "I don't know", ask other checks for an answer
    no_decision = enum.auto()


class RetryCheckFlags(enum.Flag):
    #: no flags (default)
    NONE = enum.auto()
    #: only run this check once per request
    RUN_ONCE = enum.auto()


# stub for mypy
class _RetryCheckFunc:
    _retry_check_flags: RetryCheckFlags


def set_retry_check_flags(flag: RetryCheckFlags) -> t.Callable[[C], C]:
    """
    A decorator for setting retry check flags on a retry check function.
    Usage:

    >>> @set_retry_check_flags(RetryCheckFlags.RUN_ONCE)
    >>> def foo(ctx): ...
    """

    def decorator(func: C) -> C:
        as_check = t.cast(_RetryCheckFunc, func)
        as_check._retry_check_flags = flag
        return func

    return decorator


# types useful for declaring RetryCheckRunner and related types
RetryCheck = t.Callable[[RetryContext], RetryCheckResult]


class RetryCheckRunner:
    """
    A RetryCheckRunner is an object responsible for running retry checks over the
    lifetime of a request. Unlike the checks or the retry context, the runner persists
    between retries. It can therefore implement special logic for checks like "only try
    this check once".

    Its primary responsibility is to answer the question "should_retry(context)?" with a
    boolean.

    It takes as its input a list of checks. Checks may be paired with flags to indicate
    their configuration options. When not paired with flags, the flags are taken to be
    "NONE".

    Supported flags:

    ``RUN_ONCE``
      The check will run at most once for a given request. Once it has run, it is
      recorded as "has_run" and will not be run again on that request.
    """

    # check configs: a list of pairs, (check, flags)
    # a check without flags is assumed to have flags=NONE
    def __init__(self, checks: list[RetryCheck]):
        self._checks: list[RetryCheck] = []
        self._check_data: dict[RetryCheck, dict[str, t.Any]] = {}
        for check in checks:
            self._checks.append(check)
            self._check_data[check] = {}

    def should_retry(self, context: RetryContext) -> bool:
        for check in self._checks:
            flags = getattr(check, "_retry_check_flags", RetryCheckFlags.NONE)

            if flags & RetryCheckFlags.RUN_ONCE:
                if self._check_data[check].get("has_run"):
                    continue
                else:
                    self._check_data[check]["has_run"] = True

            result = check(context)
            log.debug(  # try to get name but don't fail if it's not a function...
                "ran retry check (%s) => %s", getattr(check, "__name__", check), result
            )
            if result is RetryCheckResult.no_decision:
                continue
            elif result is RetryCheckResult.do_not_retry:
                return False
            else:
                return True

        # fallthrough: don't retry any request which isn't marked for retry
        return False
