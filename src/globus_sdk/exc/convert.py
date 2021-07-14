import requests

from .base import GlobusError

# Wrappers around requests exceptions, so the SDK is somewhat independent from details
# about requests


class NetworkError(GlobusError):
    """
    Error communicating with the REST API server.

    Holds onto original exception data, but also takes a message
    to explain potentially confusing or inconsistent exceptions passed to us
    """

    def __init__(self, msg, exc, *args, **kw):
        super().__init__(msg)
        self.underlying_exception = exc


class GlobusTimeoutError(NetworkError):
    """The REST request timed out."""


class GlobusConnectionTimeoutError(GlobusTimeoutError):
    """The request timed out during connection establishment.
    These errors are safe to retry."""


class GlobusConnectionError(NetworkError):
    """A connection error occured while making a REST request."""


def convert_request_exception(exc):
    """Converts incoming requests.Exception to a Globus NetworkError"""

    if isinstance(exc, requests.ConnectTimeout):
        return GlobusConnectionTimeoutError("ConnectTimeoutError on request", exc)
    if isinstance(exc, requests.Timeout):
        return GlobusTimeoutError("TimeoutError on request", exc)
    elif isinstance(exc, requests.ConnectionError):
        return GlobusConnectionError("ConnectionError on request", exc)
    else:
        return NetworkError("NetworkError on request", exc)
