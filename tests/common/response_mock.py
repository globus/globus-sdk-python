import json
from unittest import mock

import requests


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


def _unpickle_pickleable_mock_response(status, state):
    x = PickleableMockResponse(status)
    x.__setstate__(state)
    return x
