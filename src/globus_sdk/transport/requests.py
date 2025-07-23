from __future__ import annotations

import contextlib
import logging
import pathlib
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
from .caller_info import RequestCallerInfo
from .retry import RetryContext
from .retry_check_runner import RetryCheckRunner
from .retry_config import RetryConfig

log = logging.getLogger(__name__)


class RequestsTransport:
    """
    The RequestsTransport handles HTTP request sending and retries.

    It receives raw request information from a client class, and then performs the
    following steps
    - encode the data in a prepared request
    - repeatedly send the request until no retry is requested by the configured hooks
    - return the last response or reraise the last exception

    If the maximum number of retries is reached, the final response or exception will
    be returned or raised.

    :param verify_ssl: Explicitly enable or disable SSL verification,
        or configure the path to a CA certificate bundle to use for SSL verification
    :param http_timeout: Explicitly set an HTTP timeout value in seconds. This parameter
        defaults to 60s but can be set via the ``GLOBUS_SDK_HTTP_TIMEOUT`` environment
        variable. Any value set via this parameter takes precedence over the environment
        variable.

    :ivar dict[str, str] headers: The headers which are sent on every request. These
        may be augmented by the transport when sending requests.
    """

    #: default maximum number of retries
    DEFAULT_MAX_RETRIES = 5

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
    ) -> t.Iterator[None]:
        """
        Temporarily adjust some of the request sending settings of the transport.
        This method works as a context manager, and will reset settings to their
        original values after it exits.

        :param verify_ssl: Explicitly enable or disable SSL verification,
            or configure the path to a CA certificate bundle to use for SSL verification
        :param http_timeout: Explicitly set an HTTP timeout value in seconds

        **Example Usage**

        This can be used with any client class to temporarily set values in the context
        of one or more HTTP requests. To increase the HTTP request timeout from the
        default of 60 to 120 seconds,

        >>> client = ...  # any client class
        >>> with client.transport.tune(http_timeout=120):
        >>>     foo = client.get_foo()

        See also: :meth:`RetryConfig.tune`.
        """
        saved_settings = (
            self.verify_ssl,
            self.http_timeout,
        )
        if verify_ssl is not None:
            if isinstance(verify_ssl, bool):
                self.verify_ssl = verify_ssl
            else:
                self.verify_ssl = str(verify_ssl)
        if http_timeout is not None:
            self.http_timeout = http_timeout
        yield
        (
            self.verify_ssl,
            self.http_timeout,
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

    def _retry_sleep(self, retry_config: RetryConfig, ctx: RetryContext) -> None:
        """
        Given a retry context, compute the amount of time to sleep and sleep that much
        This is always the minimum of the backoff (run on the context) and the
        ``max_sleep``.

        :param ctx: The context object which describes the state of the request and the
            retries which may already have been attempted.
        """
        sleep_period = min(retry_config.backoff(ctx), retry_config.max_sleep)
        log.debug(
            "request retry_sleep(%s) [max=%s]",
            sleep_period,
            retry_config.max_sleep,
        )
        time.sleep(sleep_period)

    def request(
        self,
        method: str,
        url: str,
        *,
        caller_info: RequestCallerInfo,
        query_params: dict[str, t.Any] | None = None,
        data: dict[str, t.Any] | list[t.Any] | str | bytes | None = None,
        headers: dict[str, str] | None = None,
        encoding: str | None = None,
        allow_redirects: bool = True,
        stream: bool = False,
    ) -> requests.Response:
        """
        Send an HTTP request

        :param url: URL for the request
        :param method: HTTP request method, as an all caps string
        :param caller_info: Contextual information about the caller of the request,
            including the authorizer and retry configuration.
        :param query_params: Parameters to be encoded as a query string
        :param headers: HTTP headers to add to the request
        :param data: Data to send as the request body. May pass through encoding.
        :param encoding: A way to encode request data. "json", "form", and "text"
            are all valid values. Custom encodings can be used only if they are
            registered with the transport. By default, strings get "text" behavior and
            all other objects get "json".
        :param allow_redirects: Follow Location headers on redirect response
            automatically. Defaults to ``True``
        :param stream: Do not immediately download the response content. Defaults to
            ``False``

        :return: ``requests.Response`` object
        """
        log.debug("starting request for %s", url)
        resp: requests.Response | None = None
        req = self._encode(method, url, query_params, data, headers, encoding)
        retry_config = caller_info.retry_config
        checker = RetryCheckRunner(caller_info.retry_config.checks)

        log.debug("transport request state initialized")
        for attempt in range(retry_config.max_retries + 1):
            log.debug("transport request retry cycle. attempt=%d", attempt)
            # add Authorization header, or (if it's a NullAuthorizer) possibly
            # explicitly remove the Authorization header
            # done fresh for each request, to handle potential for refreshed credentials
            self._set_authz_header(caller_info.authorizer, req)

            ctx = RetryContext(attempt, caller_info=caller_info)
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
                if attempt >= retry_config.max_retries or not checker.should_retry(ctx):
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
            if attempt < retry_config.max_retries:
                log.debug("under attempt limit, will sleep")
                self._retry_sleep(retry_config, ctx)
        if resp is None:
            raise ValueError("Somehow, retries ended without a response")
        log.warning("request reached max retries, done (fail, response)")
        return resp
