import abc
import logging
from typing import Mapping, Optional

log = logging.getLogger(__name__)


class GlobusResponse(abc.ABC):
    """
    A GlobusResponse is an abstract class which defines ``__getitem__``,
    ``__contains__``, and ``get()`` with respect to some inner ``data``.

    When ``data`` is not ``None``, these methods have their meanings defined by the
    inner data object iself. Otherwise, ``__contains__`` is always False,
    ``__getitem__`` raises a ValueError, and ``get()`` always returns the default.
    """

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.data!r})"

    def __getitem__(self, key):
        # force evaluation of the data property outside of the upcoming
        # try-catch so that we don't accidentally catch TypeErrors thrown
        # during the getter function itself
        data = self.data
        try:
            return data[key]
        except TypeError:
            log.error(
                f"Can't index into responses with underlying data of type {type(data)}"
            )
            # re-raise with an altered message and error type -- the issue is that
            # whatever data is in the response doesn't support indexing (e.g. a response
            # that is just an integer, parsed as json)
            #
            # "type" is ambiguous, but we don't know if it's the fault of the
            # class at large, or just a particular call's `data` property
            raise ValueError("This type of response data does not support indexing.")

    def __contains__(self, item):
        """
        ``x in response`` is an alias for ``x in response.data``
        """
        if self.data is None:
            return False
        return item in self.data

    def get(self, key, default=None):
        """
        ``get`` is just an alias for ``data.get(key, default)``, but with the added
        check that if ``data`` is ``None``, it returns the default.
        """
        if self.data is None:
            return default
        # NB: `default` is provided as a positional because the native dict type
        # doesn't recognize a keyword argument `default`
        return self.data.get(key, default)

    @property
    @abc.abstractmethod
    def data(self) -> Optional[Mapping]:
        ...


class GlobusHTTPResponse(GlobusResponse):
    """
    Response object that wraps an HTTP response from the underlying HTTP
    library. If the response is JSON, the parsed data will be available in
    ``data``, otherwise ``data`` will be ``None`` and ``text`` should
    be used instead.

    The most common response data is a JSON dictionary. To make
    handling this type of response as seemless as possible, the
    ``GlobusHTTPResponse`` object implements the immutable mapping protocol for
    dict-style access. This is just an alias for access to the underlying data.

    If ``data`` is not a dictionary, item access will raise ``TypeError``.

    >>> print("Response ID": r["id"]) # alias for r.data["id"]

    :ivar http_status: HTTP status code returned by the server (int)
    :ivar content_type: Content-Type header returned by the server (str)
    :ivar client: The client instance which made the request
    """

    def __init__(self, http_response, client):
        self._response = http_response

        # JSON decoding may raise a ValueError due to an invalid JSON
        # document. In the case of trying to fetch the "data" on an HTTP
        # response, this means we didn't get a JSON response.
        # store this as None, as in "no data"
        #
        # if the caller *really* wants the raw body of the response, they can
        # always use `text`
        try:
            self._parsed_json = http_response.json()
        except ValueError:
            log.warning("response data did not parse as JSON, data=None")
            self._parsed_json = None

        # NB: the word 'code' is confusing because we use it in the
        # error body, and status_code is not much better. http_code, or
        # http_status_code if we wanted to be really explicit, is
        # clearer, but less consistent with requests (for better and
        # worse).
        self.http_status = http_response.status_code
        self.content_type = http_response.headers.get("Content-Type")
        self.client = client

    @property
    def data(self):
        return self._parsed_json

    @property
    def text(self):
        """The raw response data as a string."""
        return self._response.text


class GlobusHTTPResponseProxy(GlobusResponse):
    """
    A proxy or wrapper object which holds a response and exposes its public attributes
    as its own. This class is useful for defining wrappers to customize an HTTP
    response.

    It is not a GlobusHTTPResponse, so
      isinstance(GlobusHTTPResponseProxy(foo), GlobusHTTPResponse) is False
    """

    def __init__(self, wrapped: GlobusHTTPResponse):
        self._wrapped = wrapped
        self.http_status = wrapped.http_status
        self.content_type = wrapped.content_type
        self.client = wrapped.client

    @property
    def data(self):
        return self._wrapped.data

    @property
    def text(self):
        return self._wrapped.text
