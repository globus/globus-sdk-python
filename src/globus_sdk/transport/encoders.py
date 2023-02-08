from __future__ import annotations

import typing as t

import requests


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
        return requests.Request(method, url, data=data, params=params, headers=headers)


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
        return requests.Request(method, url, json=data, params=params, headers=headers)


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
        return requests.Request(method, url, data=data, params=params, headers=headers)
