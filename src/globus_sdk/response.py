from __future__ import annotations

import collections.abc
import json
import logging
import typing as t

from requests import Response

from globus_sdk import _guards

log = logging.getLogger(__name__)

if t.TYPE_CHECKING:
    import globus_sdk


class GlobusHTTPResponse:
    """
    Response object that wraps an HTTP response from the underlying HTTP
    library. If the response is JSON, the parsed data will be available in
    ``data``, otherwise ``data`` will be ``None`` and ``text`` should
    be used instead.

    The most common response data is a JSON dictionary. To make
    handling this type of response as seamless as possible, the
    ``GlobusHTTPResponse`` object implements the immutable mapping protocol for
    dict-style access. This is just an alias for access to the underlying data.

    If the response data is not a dictionary or list, item access will raise
    ``TypeError``.

    >>> print("Response ID": r["id"]) # alias for r.data["id"]

    :ivar client: The client instance which made the request
    """

    def __init__(
        self,
        response: Response | GlobusHTTPResponse,
        client: globus_sdk.BaseClient | None = None,
    ):
        # init on a GlobusHTTPResponse: we are wrapping this data
        # the _response is None
        if isinstance(response, GlobusHTTPResponse):
            if client is not None:
                raise ValueError("Redundant client with wrapped response")
            self._wrapped: GlobusHTTPResponse | None = response
            self._response: Response | None = None
            self.client: globus_sdk.BaseClient = self._wrapped.client

            # copy parsed JSON data off of '_wrapped'
            self._parsed_json: t.Any = self._wrapped._parsed_json

        # init on a Response object, this is the "normal" case
        # _wrapped is None
        else:
            if client is None:
                raise ValueError("Missing client with normal response")
            self._wrapped = None
            self._response = response
            self.client = client

            # JSON decoding may raise a ValueError due to an invalid JSON
            # document. In the case of trying to fetch the "data" on an HTTP
            # response, this means we didn't get a JSON response.
            # store this as None, as in "no data"
            #
            # if the caller *really* wants the raw body of the response, they can
            # always use `text`
            try:
                self._parsed_json = self._response.json()
            except ValueError:
                log.warning("response data did not parse as JSON, data=None")
                self._parsed_json = None

    @property
    def _raw_response(self) -> Response:
        # this is an internal property which traverses any series of wrapped responses
        # until reaching a requests response object
        if self._response is not None:
            return self._response
        elif self._wrapped is not None:
            return self._wrapped._raw_response
        else:  # unreachable  # pragma: no cover
            raise ValueError("could not find an inner response object")

    @property
    def http_status(self) -> int:
        """The HTTP response status, as an integer."""
        return self._raw_response.status_code

    @property
    def http_reason(self) -> str:
        """
        The HTTP reason string from the response.

        This is the part of the status line after the status code, and typically is a
        string description of the status. If the status line is
        ``HTTP/1.1 200 OK``, then this is the string ``"OK"``.
        """
        return self._raw_response.reason

    @property
    def headers(self) -> t.Mapping[str, str]:
        """
        The HTTP response headers as a case-insensitive mapping.

        For example, ``headers["Content-Length"]`` and ``headers["content-length"]`` are
        treated as equivalent.
        """
        return self._raw_response.headers

    @property
    def content_type(self) -> str | None:
        return self.headers.get("Content-Type")

    @property
    def text(self) -> str:
        """The raw response data as a string."""
        return self._raw_response.text

    @property
    def binary_content(self) -> bytes:
        """
        The raw response data in bytes.
        """
        return self._raw_response.content

    @property
    def data(self) -> t.Any:
        return self._parsed_json

    def get(self, key: str, default: t.Any = None) -> t.Any:
        """
        ``get`` is just an alias for ``data.get(key, default)``, but with the added
        checks that if ``data`` is ``None`` or a list, it returns the default.
        """
        if _guards.is_optional(self.data, list):
            return default
        # NB: `default` is provided as a positional because the native dict type
        # doesn't recognize a keyword argument `default`
        return self.data.get(key, default)

    def __str__(self) -> str:
        """The default __str__ for a response assumes that the data is valid
        JSON-dump-able."""
        if self.data is not None:
            return json.dumps(self.data, indent=2, separators=(",", ": "))
        return self.text

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.text})"

    def __getitem__(self, key: str | int | slice) -> t.Any:
        # force evaluation of the data property outside of the upcoming
        # try-catch so that we don't accidentally catch TypeErrors thrown
        # during the getter function itself
        data = self.data
        try:
            return data[key]
        except TypeError as err:
            log.error(
                f"Can't index into responses with underlying data of type {type(data)}"
            )
            # re-raise with an altered message and error type -- the issue is that
            # whatever data is in the response doesn't support indexing (e.g. a response
            # that is just an integer, parsed as json)
            #
            # "type" is ambiguous, but we don't know if it's the fault of the
            # class at large, or just a particular call's `data` property
            raise ValueError(
                "This type of response data does not support indexing."
            ) from err

    def __contains__(self, item: t.Any) -> bool:
        """
        ``x in response`` is an alias for ``x in response.data``
        """
        if self.data is None:
            return False
        return item in self.data

    def __bool__(self) -> bool:
        """
        ``bool(response)`` is an alias for ``bool(response.data)``
        """
        return bool(self.data)


class IterableResponse(GlobusHTTPResponse):
    """This response class adds an __iter__ method on an 'iter_key' variable.
    The assumption is that iter produces dicts or dict-like mappings."""

    default_iter_key: t.ClassVar[str]
    iter_key: str

    def __init__(
        self,
        response: Response | GlobusHTTPResponse,
        client: globus_sdk.BaseClient | None = None,
        *,
        iter_key: str | None = None,
    ) -> None:
        if not hasattr(self, "default_iter_key"):
            raise TypeError(
                "Cannot instantiate an iterable response from a class "
                "which does not define a default iteration key."
            )
        iter_key = iter_key if iter_key is not None else self.default_iter_key
        self.iter_key = iter_key
        super().__init__(response, client)

    def __iter__(self) -> t.Iterator[t.Mapping[t.Any, t.Any]]:
        if not isinstance(self.data, dict):
            raise TypeError(
                "Cannot iterate on IterableResponse data when "
                f"type is '{type(self.data).__name__}'"
            )
        return iter(self.data[self.iter_key])


class ArrayResponse(GlobusHTTPResponse):
    """This response class adds an ``__iter__`` method which assumes that the top-level
    data of the response is a JSON array."""

    def __iter__(self) -> t.Iterator[t.Any]:
        if not isinstance(self.data, list):
            raise TypeError(
                "Cannot iterate on ArrayResponse data when "
                f"type is '{type(self.data).__name__}'"
            )
        return iter(self.data)

    def __len__(self) -> int:
        """
        ``len(response)`` is an alias for ``len(response.data)``
        """
        if not isinstance(self.data, collections.abc.Sequence):
            raise TypeError(
                "Cannot take len() on ArrayResponse data when "
                f"type is '{type(self.data).__name__}'"
            )
        return len(self.data)
