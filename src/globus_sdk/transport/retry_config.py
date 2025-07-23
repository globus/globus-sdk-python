from __future__ import annotations

import contextlib
import dataclasses
import random
import typing as t

from .retry import RetryCheckCollection, RetryContext


def _exponential_backoff(ctx: RetryContext) -> float:
    # respect any explicit backoff set on the context
    if ctx.backoff is not None:
        return ctx.backoff
    # exponential backoff with jitter
    return t.cast(float, (0.25 + 0.5 * random.random()) * (2**ctx.attempt))


@dataclasses.dataclass
class RetryConfig:
    """
    Configuration for a client which is going to retry requests.

    :param max_retries: The maximum number of retries allowed.
    :param max_sleep: The maximum sleep time between retries (in seconds). If the
        computed sleep time or the backoff requested by a retry check exceeds this
        value, this amount of time will be used instead.
    :param backoff: A function which determines how long to sleep between calls
        based on the RetryContext. Defaults to exponential backoff with jitter based on
        the context ``attempt`` number.
    :param retry_after_status_codes: HTTP status codes for responses which may have
        a Retry-After header.
    :param transient_error_status_codes: HTTP status codes for error responses which
        should generally be retried.
    :param expired_authorization_status_codes: HTTP status codes indicating that
        authorization info was missing or expired.
    :param checks: The check callbacks which will run in order to evaluate
        responses and exceptions, as a ``RetryCheckCollection``.
    """

    max_retries: int = 5
    max_sleep: float | int = 10
    backoff: t.Callable[[RetryContext], float] = _exponential_backoff
    retry_after_status_codes: tuple[int, ...] = (429, 503)
    transient_error_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504)
    expired_authorization_status_codes: tuple[int, ...] = (401,)

    checks: RetryCheckCollection = dataclasses.field(
        default_factory=RetryCheckCollection
    )

    @contextlib.contextmanager
    def tune(
        self,
        *,
        backoff: t.Callable[[RetryContext], float] | None = None,
        max_sleep: float | int | None = None,
        max_retries: int | None = None,
    ) -> t.Iterator[None]:
        """
        Temporarily adjust some of the request retry settings.
        This method works as a context manager, and will reset settings to their
        original values after it exits.

        :param backoff: A function which determines how long to sleep between
            calls based on the RetryContext
        :param max_sleep: The maximum sleep time between retries (in seconds). If the
            computed sleep time or the backoff requested by a retry check exceeds this
            value, this amount of time will be used instead
        :param max_retries: The maximum number of retries allowed by this transport

        **Example Usage**

        This can be used with any client class to temporarily set values in the context
        of one or more HTTP requests. For example, to disable retries:

        >>> client = ...  # any client class
        >>> with client.retry_config.tune(max_retries=0):
        >>>     foo = client.get_foo()

        See also: :meth:`RequestsTransport.tune`.
        """
        saved_settings = (
            self.backoff,
            self.max_sleep,
            self.max_retries,
        )
        if backoff is not None:
            self.backoff = backoff
        if max_sleep is not None:
            self.max_sleep = max_sleep
        if max_retries is not None:
            self.max_retries = max_retries
        yield
        (
            self.backoff,
            self.max_sleep,
            self.max_retries,
        ) = saved_settings
