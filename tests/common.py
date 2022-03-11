"""
Common use helpers and utilities for all tests to leverage.
Not so disorganized as a "utils" module and not so refined as a public package.
"""
import inspect
import json
import os
from unittest import mock

import requests
import responses

import globus_sdk
from globus_sdk import utils

# constants

GO_EP1_ID = "ddb59aef-6d04-11e5-ba46-22000b92c6ec"
GO_EP2_ID = "ddb59af0-6d04-11e5-ba46-22000b92c6ec"
# TODO: stop using EP3 once EP1 and EP2 support symlinks
GO_EP3_ID = "4be6107f-634d-11e7-a979-22000bf2d287"
GO_S3_ID = "cf9bcaa5-6d04-11e5-ba46-22000b92c6ec"
GO_EP1_SERVER_ID = 207976

# end constants


def register_api_route(
    service, path, method=responses.GET, adding_headers=None, replace=False, **kwargs
):
    """
    Handy wrapper for adding URIs to the response mock state.
    """
    base_url_map = {
        "auth": "https://auth.globus.org/",
        "nexus": "https://nexus.api.globusonline.org/",
        "groups": "https://groups.api.globus.org/",
        "transfer": "https://transfer.api.globus.org/v0.10",
        "search": "https://search.api.globus.org/",
        "gcs": "https://abc.xyz.data.globus.org/api/",
    }
    assert service in base_url_map
    base_url = base_url_map.get(service)
    full_url = utils.slash_join(base_url, path)

    # can set it to `{}` explicitly to clear the default
    if adding_headers is None:
        adding_headers = {"Content-Type": "application/json"}

    if replace:
        responses.replace(
            method, full_url, headers=adding_headers, match_querystring=None, **kwargs
        )
    else:
        responses.add(
            method, full_url, headers=adding_headers, match_querystring=None, **kwargs
        )


def register_api_route_fixture_file(service, path, filename, **kwargs):
    """
    register an API route to serve the contents of a file, given the name of
    that file in a `fixture_data` directory, adjacent to the current (calling)
    module

    i.e. in a dir like this:
      path/to/tests
      ├── test_mod.py
      └── fixture_data
          └── dat.txt

    you can call
    >>> register_api_route_fixture_file('transfer', '/foo', 'dat.txt')

    in `test_mod.py`

    it will "do the right thing" and find the abspath to dat.txt , and
    load the contents of that file as the response for '/foo'
    """
    # get calling frame
    frm = inspect.stack()[1]
    # get filename from frame, make it absolute
    modpath = os.path.abspath(frm[1])

    abspath = os.path.join(os.path.dirname(modpath), "fixture_data", filename)
    with open(abspath, "rb") as f:
        body = f.read()

    register_api_route(service, path, body=body, **kwargs)


def _unpickle_pickleable_mock_response(status, state):
    x = PickleableMockResponse(status)
    x.__setstate__(state)
    return x


class PickleableMockResponse(mock.NonCallableMock):
    """
    Custom Mock class which implements __setstate__ and __getstate__ so that it
    can be pickled and unpickled correctly -- thus avoiding issues with the
    tests which pickle/unpickle clients and responses (and thereby, their inner
    objects).

    The only attributes which survive the pickle/unpickle process are those
    with defined treatment in the __getstate__ and __setstate__ methods.


    NOTE: It also has to set `__class__` explicitly, which can break some mock
    functionality.


    I've tried various workarounds using copyreg to put in a custom serializer
    for things with a __class__ of requests.Response which checks to see if
    type(obj) is PickleableMockResponse and *all kinds of stuff*. None of it
    seems to work, so this is the best thing I could figure out for now.
    - Stephen (2018-09-07)
    """

    def __init__(
        self, status_code, json_body=None, text=None, headers=None, *args, **kwargs
    ):
        kwargs["spec"] = requests.Response
        super().__init__(*args, **kwargs)
        self.__class__ = PickleableMockResponse

        # after mock initialization, setup various explicit attributes
        self.status_code = status_code

        self.headers = headers or {"Content-Type": "application/json"}

        self._json_body = json_body

        self.text = text or (json.dumps(json_body) if json_body else "")

    def json(self):
        if self._json_body is not None:
            return self._json_body
        else:
            raise ValueError("globus sdk mock value error")

    def __getstate__(self):
        """Custom getstate discards most of the magical mock stuff"""
        keys = ["headers", "text", "_json_body", "status_code"]
        return {k: self.__dict__[k] for k in keys}

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __reduce__(self):
        return (
            _unpickle_pickleable_mock_response,
            (self.status_code, self.__getstate__()),
        )


def make_response(
    response_class=None,
    status=200,
    headers=None,
    json_body=None,
    text=None,
    client=None,
):
    """
    Construct and return an SDK response object with a mocked requests.Response

    Unlike mocking of an API route, this is meant for unit testing in which we
    want to directly create the response.
    """
    r = PickleableMockResponse(status, headers=headers, json_body=json_body, text=text)
    http_res = globus_sdk.GlobusHTTPResponse(
        r, client=client if client is not None else mock.Mock()
    )
    if response_class is not None:
        return response_class(http_res)
    return http_res
