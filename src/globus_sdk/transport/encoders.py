from __future__ import annotations

import enum
import typing as t
import uuid

import requests

from globus_sdk._missing import MISSING, filter_missing


class RequestEncoder:
    """
    A RequestEncoder takes input parameters and outputs a requests.Requests object.

    The default encoder requires that the data is text and is a no-op. It can also be
    referred to as the ``"text"`` encoder.
    """

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
        return requests.Request(
            method,
            url,
            data=self._prepare_data(data),
            params=self._prepare_params(params),
            headers=self._prepare_headers(headers),
        )

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


class JSONRequestEncoder(RequestEncoder):
    """
    This encoder prepares the data as JSON. It also ensures that content-type is set, so
    that APIs requiring a content-type of "application/json" are able to read the data.
    """

    def encode(
        self,
        method: str,
        url: str,
        params: dict[str, t.Any] | None,
        data: t.Any,
        headers: dict[str, str],
    ) -> requests.Request:
        if data is not None:
            headers = {"Content-Type": "application/json", **headers}
        return requests.Request(
            method,
            url,
            json=self._prepare_data(data),
            params=self._prepare_params(params),
            headers=self._prepare_headers(headers),
        )


class FormRequestEncoder(RequestEncoder):
    """
    This encoder formats data as a form-encoded body. It requires that the input data is
    a dict -- any other datatype will result in errors.
    """

    def encode(
        self,
        method: str,
        url: str,
        params: dict[str, t.Any] | None,
        data: t.Any,
        headers: dict[str, str],
    ) -> requests.Request:
        if not isinstance(data, dict):
            raise TypeError("FormRequestEncoder cannot encode non-dict data")
        return requests.Request(
            method,
            url,
            data=self._prepare_data(data),
            params=self._prepare_params(params),
            headers=self._prepare_headers(headers),
        )
