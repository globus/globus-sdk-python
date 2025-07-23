from __future__ import annotations

import enum
import typing as t

import requests

if t.TYPE_CHECKING:
    from .caller_info import RequestCallerInfo

C = t.TypeVar("C", bound=t.Callable[..., t.Any])


# alias useful for declaring retry-related types
RetryCheck = t.Callable[["RetryContext"], "RetryCheckResult"]


class RetryContext:
    """
    The RetryContext is an object passed to retry checks in order to determine whether
    or not a request should be retried. The context is constructed after each request,
    regardless of success or failure.

    If an exception was raised, the context will contain that exception object.
    Otherwise, the context will contain a response object. Exactly one of ``response``
    or ``exception`` will be present.

    :param attempt: The request attempt number, starting at 0.
    :param caller_info: Contextual information about the caller, including authorizer
    :param response: The response on a successful request
    :param exception: The error raised when trying to send the request
    """

    def __init__(
        self,
        attempt: int,
        *,
        caller_info: RequestCallerInfo,
        response: requests.Response | None = None,
        exception: Exception | None = None,
    ) -> None:
        # retry attempt number
        self.attempt = attempt
        # caller info provides contextual information about the request
        self.caller_info = caller_info
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

    :param flag: The flag to set on the check
    """

    def decorator(func: C) -> C:
        as_check = t.cast(_RetryCheckFunc, func)
        as_check._retry_check_flags = flag
        return func

    return decorator


class RetryCheckCollection:
    """
    A RetryCheckCollection is an ordered collection of retry checks which are
    used to determine whether or not a request should be retried.

    Checks are stored in registration order.

    Notably, the collection does not decide
    - how many times a request should retry
    - how or how long the call should wait between attempts
      (except via the backoff which may be set)
    - what kinds of request parameters (e.g., timeouts) are used

    It *only* contains ``RetryCheck`` methods which can look at a response or
    error and decide whether or not to retry.
    """

    def __init__(self) -> None:
        self._data: list[RetryCheck] = []

    def register_check(self, func: RetryCheck) -> RetryCheck:
        """
        Register a retry check with this policy.

        A retry checker is a callable responsible for implementing
        `check(RetryContext) -> RetryCheckResult`

        `check` should *not* perform any sleeps or delays.
        Multiple checks should be chainable and callable in any order.

        :param func: The function or other callable to register as a retry check
        """
        self._data.append(func)
        return func

    def register_many_checks(self, funcs: t.Iterable[RetryCheck]) -> None:
        """
        Register all checks in a collection of checks.

        :param funcs: An iterable collection of retry check callables
        """
        for f in funcs:
            self.register_check(f)

    def __iter__(self) -> t.Iterator[RetryCheck]:
        yield from self._data

    def __len__(self) -> int:
        return len(self._data)
