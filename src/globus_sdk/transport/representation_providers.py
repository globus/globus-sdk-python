from __future__ import annotations

import enum
import typing as t
import uuid

from globus_sdk._internal import orjson_compat
from globus_sdk._missing import MISSING, filter_missing

if t.TYPE_CHECKING:
    import requests


class RequestsRepresentationProvider:
    """
    A ``RequestsRepresentationProvider`` defines transformations of data to and from
    ``requests`` datatypes, for a given representation of the data -- primarily the
    media type.

    Providers must have two methods:

    - ``encode()`` takes input parameters and outputs a requests.Requests object

    - ``decode_body()`` takes a requests.Response object and reads the body
    """

    def encode(
        self,
        method: str,
        url: str,
        params: dict[str, t.Any] | None,
        data: t.Any,
        headers: dict[str, str],
    ) -> requests.Request:
        """
        Formulate a ``requests.Request``, defaulting to plain-text for the body.

        :param method: the HTTP method name
        :param url: the full URL for the request
        :param params: query parameters, as a dict
        :param data: the body, as a type which this provider can encode
        :param headers: HTTP headers, as a dict
        """
        import requests

        return requests.Request(
            method,
            url,
            data=self._prepare_data(data),
            params=self._prepare_params(params),
            headers=self._prepare_headers(headers),
        )

    def decode_body(self, response: requests.Response) -> t.Any:
        """
        Read a response as text.

        :param response: the ``requests.Response`` to read
        """
        return response.text

    def _format_primitive(self, value: t.Any) -> t.Any:
        """
        Transformations for primitive values (e.g. stringifiable items) for query
        params, headers, and body elements.

        Transforms data as follows:

            x: UUID -> str(x)
            x: Enum -> x.value
            x: _    -> x
        """
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, enum.Enum):
            return value.value
        return value

    def _prepare_params(
        self, params: dict[str, t.Any] | None
    ) -> dict[str, t.Any] | None:
        """
        Prepare the query params for a request.

        Filters out MISSING and formats primitives.
        """
        if params is None:
            return None
        return filter_missing({k: self._format_primitive(v) for k, v in params.items()})

    def _prepare_headers(
        self, headers: dict[str, t.Any] | None
    ) -> dict[str, t.Any] | None:
        """
        Prepare the headers for a request.

        Filters out MISSING and formats primitives.
        """
        if headers is None:
            return None
        return filter_missing(
            {k: self._format_primitive(v) for k, v in headers.items()}
        )

    def _prepare_data(self, data: t.Any) -> t.Any:
        """
        Prepare the data (body) for a request.

        If the body is a dict, list, or tuple, it will be recursively processed to
        filter out MISSING and format primitives.

        Otherwise, it is returned as-is.
        """
        if isinstance(data, dict):
            return filter_missing({k: self._prepare_data(v) for k, v in data.items()})
        elif isinstance(data, (list, tuple)):
            return [self._prepare_data(x) for x in data if x is not MISSING]
        else:
            return self._format_primitive(data)


class RequestsPlainTextProvider(RequestsRepresentationProvider):
    """The plain-text provider ensures that the body is text."""

    def encode(
        self,
        method: str,
        url: str,
        params: dict[str, t.Any] | None,
        data: t.Any,
        headers: dict[str, str],
    ) -> requests.Request:
        if not isinstance(data, (str, bytes)):
            raise TypeError(
                "Cannot encode non-text in a text request. "
                "Either manually encode the data or use `encoding=form|json` to "
                "correctly format this data."
            )
        return super().encode(
            method,
            url,
            data=self._prepare_data(data),
            params=self._prepare_params(params),
            headers=self._prepare_headers(headers),  # type: ignore[arg-type]
        )


class RequestsJsonProvider(RequestsRepresentationProvider):
    """
    This provider prepares request data as JSON. It also ensures that content-type is
    set, so that APIs requiring a content-type of "application/json" are able to read
    the data.

    When decoding response bodies, it decodes them as JSON content.

    If the ``orjson`` library is installed, it will be used to provide accelerated
    encoding and decoding.
    """

    def encode(
        self,
        method: str,
        url: str,
        params: dict[str, t.Any] | None,
        data: t.Any,
        headers: dict[str, str],
    ) -> requests.Request:
        import requests

        if data is not None:
            headers = {"Content-Type": "application/json", **headers}

        # use `orjson` if it's available
        if orjson_compat.ORJSON_AVAILABLE:
            body = prepared = self._prepare_data(data)
            if body is not None:
                body = orjson_compat.dumps(body)

            return requests.Request(
                method,
                url,
                # passing both 'data' and 'json' ensures that both attributes are set,
                # but only the 'data' will be used for the body of the prepared request
                data=body,
                json=prepared,
                params=self._prepare_params(params),
                headers=self._prepare_headers(headers),
            )
        else:
            return requests.Request(
                method,
                url,
                json=self._prepare_data(data),
                params=self._prepare_params(params),
                headers=self._prepare_headers(headers),
            )

    def decode_body(self, response: requests.Response) -> t.Any:
        if orjson_compat.ORJSON_AVAILABLE:
            return orjson_compat.loads(response.content)
        else:
            return response.json()


class RequestsHttpFormProvider(RequestsRepresentationProvider):
    """
    This provider prepares request data as a form-encoded body.

    It requires that the input data is a dict -- any other datatype will result in
    errors.

    Decoding raises an error, as decoding with this format is not implemented.
    """

    def encode(
        self,
        method: str,
        url: str,
        params: dict[str, t.Any] | None,
        data: t.Any,
        headers: dict[str, str] | None,
    ) -> requests.Request:
        import requests

        if not isinstance(data, dict):
            raise TypeError("HttpFormProvider cannot encode non-dict data")
        return requests.Request(
            method,
            url,
            data=self._prepare_data(data),
            params=self._prepare_params(params),
            headers=self._prepare_headers(headers),
        )

    def decode_body(self, response: requests.Response) -> t.Any:
        raise NotImplementedError(
            "globus-sdk does not currently implement form body decoding."
        )
