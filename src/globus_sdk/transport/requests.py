from __future__ import annotations

import contextlib
import logging
import pathlib
import random
import time
import typing as t

import requests

from globus_sdk import __version__, config, exc
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.transport.encoders import (
    FormRequestEncoder,
    JSONRequestEncoder,
    RequestEncoder,
)

from ._clientinfo import GlobusClientInfo
from .retry import (
    RetryCheck,
    RetryCheckFlags,
    RetryCheckResult,
    RetryCheckRunner,
    RetryContext,
    set_retry_check_flags,
)

log = logging.getLogger(__name__)


def _parse_retry_after(response: requests.Response) -> int | None:
    val = response.headers.get("Retry-After")
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None


def _exponential_backoff(ctx: RetryContext) -> float:
    # respect any explicit backoff set on the context
    if ctx.backoff is not None:
        return ctx.backoff
    # exponential backoff with jitter
    return t.cast(float, (0.25 + 0.5 * random.random()) * (2**ctx.attempt))


class RequestsTransport:
    """
    The RequestsTransport handles HTTP request sending and retries.

    It receives raw request information from a client class, and then performs the
    following steps
    - encode the data in a prepared request
    - repeatedly send the request until no retry is requested
    - return the last response or reraise the last exception

    Retry checks are registered as hooks on the Transport. Additional hooks can be
    passed to the constructor via `retry_checks`. Or hooks can be added to an existing
    transport via a decorator.

    If the maximum number of retries is reached, the final response or exception will
    be returned or raised.

    :param verify_ssl: Explicitly enable or disable SSL verification,
        or configure the path to a CA certificate bundle to use for SSL verification
    :param http_timeout: Explicitly set an HTTP timeout value in seconds. This parameter
        defaults to 60s but can be set via the ``GLOBUS_SDK_HTTP_TIMEOUT`` environment
        variable. Any value set via this parameter takes precedence over the environment
        variable.
    :param retry_backoff: A function which determines how long to sleep between calls
        based on the RetryContext. Defaults to exponential backoff with jitter based on
        the context ``attempt`` number.
    :param retry_checks: A list of initial retry checks. Any hooks registered,
        including the default hooks, will run after these checks.
    :param max_sleep: The maximum sleep time between retries (in seconds). If the
        computed sleep time or the backoff requested by a retry check exceeds this
        value, this amount of time will be used instead
    :param max_retries: The maximum number of retries allowed by this transport

    :ivar dict[str, str] headers: The headers which are sent on every request. These
        may be augmented by the transport when sending requests.
    """

    #: default maximum number of retries
    DEFAULT_MAX_RETRIES = 5

    #: status codes for responses which may have a Retry-After header
    RETRY_AFTER_STATUS_CODES: tuple[int, ...] = (429, 503)
    #: status codes for error responses which should generally be retried
    TRANSIENT_ERROR_STATUS_CODES: tuple[int, ...] = (429, 500, 502, 503, 504)
    #: status codes indicating that authorization info was missing or expired
    EXPIRED_AUTHORIZATION_STATUS_CODES: tuple[int, ...] = (401,)

    #: the encoders are a mapping of encoding names to encoder objects
    encoders: dict[str, RequestEncoder] = {
        "text": RequestEncoder(),
        "json": JSONRequestEncoder(),
        "form": FormRequestEncoder(),
    }

    BASE_USER_AGENT = f"globus-sdk-py-{__version__}"

    def __init__(
        self,
        verify_ssl: bool | str | pathlib.Path | None = None,
        http_timeout: float | None = None,
        retry_backoff: t.Callable[[RetryContext], float] = _exponential_backoff,
        retry_checks: list[RetryCheck] | None = None,
        max_sleep: float | int = 10,
        max_retries: int | None = None,
    ) -> None:
        self.session = requests.Session()
        self.verify_ssl = config.get_ssl_verify(verify_ssl)
        self.http_timeout = config.get_http_timeout(http_timeout)
        self._user_agent = self.BASE_USER_AGENT
        self.globus_client_info: GlobusClientInfo = GlobusClientInfo(
            update_callback=self._handle_clientinfo_update
        )
        self.headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "X-Globus-Client-Info": self.globus_client_info.format(),
        }

        # retry parameters
        self.retry_backoff = retry_backoff
        self.max_sleep = max_sleep
        self.max_retries = (
            max_retries if max_retries is not None else self.DEFAULT_MAX_RETRIES
        )
        self.retry_checks = list(retry_checks if retry_checks else [])  # copy
        # register internal checks
        self.register_default_retry_checks()

    def close(self) -> None:
        """
        Closes all resources owned by the transport, primarily the underlying
        network session.
        """
        self.session.close()

    @property
    def user_agent(self) -> str:
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        """
        Set the ``user_agent`` and update the ``User-Agent`` header in ``headers``.

        :param value: The new user-agent string to set (after the base user-agent)
        """
        self._user_agent = f"{self.BASE_USER_AGENT}/{value}"
        self.headers["User-Agent"] = self._user_agent

    def _handle_clientinfo_update(
        self,
        info: GlobusClientInfo,  # pylint: disable=unused-argument
    ) -> None:
        """
        When the attached ``GlobusClientInfo`` is updated, write it back into
        ``headers``.

        If the client info is cleared, it will be removed from the headers.
        """
        formatted = self.globus_client_info.format()
        if formatted:
            self.headers["X-Globus-Client-Info"] = formatted
        else:
            # discard the element, so that this can be invoked multiple times
            self.headers.pop("X-Globus-Client-Info", None)

    @contextlib.contextmanager
    def tune(
        self,
        *,
        verify_ssl: bool | str | pathlib.Path | None = None,
        http_timeout: float | None = None,
        retry_backoff: t.Callable[[RetryContext], float] | None = None,
        max_sleep: float | int | None = None,
        max_retries: int | None = None,
    ) -> t.Iterator[None]:
        """
        Temporarily adjust some of the request sending settings of the transport.
        This method works as a context manager, and will reset settings to their
        original values after it exits.

        In particular, this can be used to temporarily adjust request-sending minutiae
        like the ``http_timeout`` used.

        :param verify_ssl: Explicitly enable or disable SSL verification,
            or configure the path to a CA certificate bundle to use for SSL verification
        :param http_timeout: Explicitly set an HTTP timeout value in seconds
        :param retry_backoff: A function which determines how long to sleep between
            calls based on the RetryContext
        :param max_sleep: The maximum sleep time between retries (in seconds). If the
            computed sleep time or the backoff requested by a retry check exceeds this
            value, this amount of time will be used instead
        :param max_retries: The maximum number of retries allowed by this transport

        **Examples**

        This can be used with any client class to temporarily set values in the context
        of one or more HTTP requests. To increase the HTTP request timeout from the
        default of 60 to 120 seconds,

        >>> client = ...  # any client class
        >>> with client.transport.tune(http_timeout=120):
        >>>     foo = client.get_foo()

        or to disable retries (note that this also disables the retry on
        expired-and-refreshed credentials):

        >>> client = ...  # any client class
        >>> with client.transport.tune(max_retries=0):
        >>>     foo = client.get_foo()
        """
        saved_settings = (
            self.verify_ssl,
            self.http_timeout,
            self.retry_backoff,
            self.max_sleep,
            self.max_retries,
        )
        if verify_ssl is not None:
            if isinstance(verify_ssl, bool):
                self.verify_ssl = verify_ssl
            else:
                self.verify_ssl = str(verify_ssl)
        if http_timeout is not None:
            self.http_timeout = http_timeout
        if retry_backoff is not None:
            self.retry_backoff = retry_backoff
        if max_sleep is not None:
            self.max_sleep = max_sleep
        if max_retries is not None:
            self.max_retries = max_retries
        yield
        (
            self.verify_ssl,
            self.http_timeout,
            self.retry_backoff,
            self.max_sleep,
            self.max_retries,
        ) = saved_settings

    def _encode(
        self,
        method: str,
        url: str,
        query_params: dict[str, t.Any] | None = None,
        data: dict[str, t.Any] | list[t.Any] | str | bytes | None = None,
        headers: dict[str, str] | None = None,
        encoding: str | None = None,
    ) -> requests.Request:
        if headers:
            headers = {**self.headers, **headers}
        else:
            headers = self.headers

        if encoding is None:
            if isinstance(data, (bytes, str)):
                encoding = "text"
            else:
                encoding = "json"

        if encoding not in self.encoders:
            raise ValueError(
                f"Unknown encoding '{encoding}' is not supported by this transport."
            )

        return self.encoders[encoding].encode(method, url, query_params, data, headers)

    def _set_authz_header(
        self, authorizer: GlobusAuthorizer | None, req: requests.Request
    ) -> None:
        if authorizer:
            authz_header = authorizer.get_authorization_header()
            if authz_header:
                req.headers["Authorization"] = authz_header
            else:
                req.headers.pop("Authorization", None)  # remove any possible value

    def _retry_sleep(self, ctx: RetryContext) -> None:
        """
        Given a retry context, compute the amount of time to sleep and sleep that much
        This is always the minimum of the backoff (run on the context) and the
        ``max_sleep``.

        :param ctx: The context object which describes the state of the request and the
            retries which may already have been attempted.
        """
        sleep_period = min(self.retry_backoff(ctx), self.max_sleep)
        log.debug("request retry_sleep(%s) [max=%s]", sleep_period, self.max_sleep)
        time.sleep(sleep_period)

    def request(
        self,
        method: str,
        url: str,
        query_params: dict[str, t.Any] | None = None,
        data: dict[str, t.Any] | list[t.Any] | str | bytes | None = None,
        headers: dict[str, str] | None = None,
        encoding: str | None = None,
        authorizer: GlobusAuthorizer | None = None,
        allow_redirects: bool = True,
        stream: bool = False,
    ) -> requests.Response:
        """
        Send an HTTP request

        :param url: URL for the request
        :param method: HTTP request method, as an all caps string
        :param query_params: Parameters to be encoded as a query string
        :param headers: HTTP headers to add to the request
        :param data: Data to send as the request body. May pass through encoding.
        :param encoding: A way to encode request data. "json", "form", and "text"
            are all valid values. Custom encodings can be used only if they are
            registered with the transport. By default, strings get "text" behavior and
            all other objects get "json".
        :param authorizer: The authorizer which is used to get or update authorization
            information for the request
        :param allow_redirects: Follow Location headers on redirect response
            automatically. Defaults to ``True``
        :param stream: Do not immediately download the response content. Defaults to
            ``False``

        :return: ``requests.Response`` object
        """
        log.debug("starting request for %s", url)
        resp: requests.Response | None = None
        req = self._encode(method, url, query_params, data, headers, encoding)
        checker = RetryCheckRunner(self.retry_checks)
        log.debug("transport request state initialized")
        for attempt in range(self.max_retries + 1):
            log.debug("transport request retry cycle. attempt=%d", attempt)
            # add Authorization header, or (if it's a NullAuthorizer) possibly
            # explicitly remove the Authorization header
            # done fresh for each request, to handle potential for refreshed credentials
            self._set_authz_header(authorizer, req)

            ctx = RetryContext(attempt, authorizer=authorizer)
            try:
                log.debug("request about to send")
                resp = ctx.response = self.session.send(
                    req.prepare(),
                    timeout=self.http_timeout,
                    verify=self.verify_ssl,
                    allow_redirects=allow_redirects,
                    stream=stream,
                )
            except requests.RequestException as err:
                log.debug("request hit error (RequestException)")
                ctx.exception = err
                if attempt >= self.max_retries or not checker.should_retry(ctx):
                    log.warning("request done (fail, error)")
                    raise exc.convert_request_exception(err)
                log.debug("request may retry (should-retry=true)")
            else:
                log.debug("request success, still check should-retry")
                if not checker.should_retry(ctx):
                    log.debug("request done (success)")
                    return resp
                log.debug("request may retry, will check attempts")

            # the request will be retried, so sleep...
            if attempt < self.max_retries:
                log.debug("under attempt limit, will sleep")
                self._retry_sleep(ctx)
        if resp is None:
            raise ValueError("Somehow, retries ended without a response")
        log.warning("request reached max retries, done (fail, response)")
        return resp

    # decorator which lets you add a check to a retry policy
    def register_retry_check(self, func: RetryCheck) -> RetryCheck:
        """
        Register a retry check with this transport.

        A retry checker is a callable responsible for implementing
        `check(RetryContext) -> RetryCheckResult`

        `check` should *not* perform any sleeps or delays.
        Multiple checks should be chainable and callable in any order.

        :param func: The function or other callable to register as a retry check
        """
        self.retry_checks.append(func)
        return func

    def register_default_retry_checks(self) -> None:
        """
        This hook is called during transport initialization. By default, it registers
        the following hooks:

        - default_check_expired_authorization
        - default_check_request_exception
        - default_check_retry_after_header
        - default_check_transient_error

        It can be overridden to register additional hooks or to remove the default
        hooks.
        """
        self.register_retry_check(self.default_check_expired_authorization)
        self.register_retry_check(self.default_check_request_exception)
        self.register_retry_check(self.default_check_retry_after_header)
        self.register_retry_check(self.default_check_transient_error)

    def default_check_request_exception(self, ctx: RetryContext) -> RetryCheckResult:
        """
        Check if a network error was encountered

        :param ctx: The context object which describes the state of the request and the
            retries which may already have been attempted.
        """
        if ctx.exception and isinstance(ctx.exception, requests.RequestException):
            return RetryCheckResult.do_retry
        return RetryCheckResult.no_decision

    def default_check_retry_after_header(self, ctx: RetryContext) -> RetryCheckResult:
        """
        Check for a retry-after header if the response had a matching status

        :param ctx: The context object which describes the state of the request and the
            retries which may already have been attempted.
        """
        if (
            ctx.response is None
            or ctx.response.status_code not in self.RETRY_AFTER_STATUS_CODES
        ):
            return RetryCheckResult.no_decision
        retry_after = _parse_retry_after(ctx.response)
        if retry_after:
            ctx.backoff = float(retry_after)
        return RetryCheckResult.do_retry

    def default_check_transient_error(self, ctx: RetryContext) -> RetryCheckResult:
        """
        Check for transient error status codes which could be resolved by retrying
        the request

        :param ctx: The context object which describes the state of the request and the
            retries which may already have been attempted.
        """
        if ctx.response is not None and (
            ctx.response.status_code in self.TRANSIENT_ERROR_STATUS_CODES
        ):
            return RetryCheckResult.do_retry
        return RetryCheckResult.no_decision

    @set_retry_check_flags(RetryCheckFlags.RUN_ONCE)
    def default_check_expired_authorization(
        self, ctx: RetryContext
    ) -> RetryCheckResult:
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
            or ctx.authorizer is None
            or ctx.response.status_code not in self.EXPIRED_AUTHORIZATION_STATUS_CODES
        ):
            return RetryCheckResult.no_decision

        # run the authorizer's handler, and 'do_retry' if the handler indicated
        # that it was able to make a change which should make the request retryable
        if ctx.authorizer.handle_missing_authorization():
            return RetryCheckResult.do_retry
        return RetryCheckResult.no_decision
