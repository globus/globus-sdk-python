import json
from collections import namedtuple
from unittest import mock

import pytest
import requests

from globus_sdk.response import GlobusHTTPResponse

_TestResponse = namedtuple("_TestResponse", ("data", "r"))


def _mk_json_response(data):
    json_response = requests.Response()
    json_response._content = json.dumps(data).encode("utf-8")
    json_response.headers["Content-Type"] = "application/json"
    return _TestResponse(data, GlobusHTTPResponse(json_response, client=mock.Mock()))


@pytest.fixture
def dict_response():
    return _mk_json_response({"label1": "value1", "label2": "value2"})


@pytest.fixture
def list_response():
    return _mk_json_response(["value1", "value2", "value3"])


@pytest.fixture
def http_no_content_type_response():
    res = requests.Response()
    assert "Content-Type" not in res.headers
    return _TestResponse(None, GlobusHTTPResponse(res, client=mock.Mock()))


@pytest.fixture
def malformed_http_response():
    malformed_response = requests.Response()
    malformed_response._content = b"{"
    malformed_response.headers["Content-Type"] = "application/json"
    return _TestResponse(
        "{", GlobusHTTPResponse(malformed_response, client=mock.Mock())
    )


@pytest.fixture
def text_http_response():
    text_data = "text data"
    text_response = requests.Response()
    text_response._content = text_data.encode("utf-8")
    text_response.headers["Content-Type"] = "text/plain"
    return _TestResponse(
        text_data, GlobusHTTPResponse(text_response, client=mock.Mock())
    )


def test_data(
    dict_response,
    list_response,
    malformed_http_response,
    text_http_response,
):
    """
    Gets the data from the GlobusResponses, confirms results
    Gets the data from each HTTPResponse, confirms expected data from json
    and None from malformed or plain text HTTP
    """
    assert dict_response.r.data == dict_response.data
    assert list_response.r.data == list_response.data
    assert malformed_http_response.r.data is None
    assert text_http_response.r.data is None


def test_str(dict_response, list_response):
    """
    Confirms that individual values are seen in stringified responses
    """
    for item in dict_response.data:
        assert item in str(dict_response.r)
    assert "nonexistent" not in str(dict_response.r)

    for item in list_response.data:
        assert item in str(list_response.r)
    assert "nonexistent" not in str(list_response.r)


def test_getitem(dict_response, list_response):
    """
    Confirms that values can be accessed from the GlobusResponse
    """
    for key in dict_response.data:
        assert dict_response.r[key] == dict_response.data[key]

    for i in range(len(list_response.data)):
        assert list_response.r[i] == list_response.data[i]


def test_contains(dict_response, list_response):
    """
    Confirms that individual values are seen in the GlobusResponse
    """
    for item in dict_response.data:
        assert item in dict_response.r
    assert "nonexistent" not in dict_response.r

    for item in list_response.data:
        assert item in list_response.r
    assert "nonexistent" not in list_response.r


def test_get(dict_response, list_response):
    """
    Gets individual values from dict response, confirms results
    Confirms list response correctly fails as non indexable
    """
    for item in dict_response.data:
        assert dict_response.r.get(item) == dict_response.data.get(item)

    with pytest.raises(AttributeError):
        list_response.r.get("value1")


def test_text(malformed_http_response, text_http_response):
    """
    Gets the text from each HTTPResponse, confirms expected results
    """
    assert malformed_http_response.r.text == "{"
    assert text_http_response.r.text == text_http_response.data


def test_no_content_type_header(http_no_content_type_response):
    """
    Response without a Content-Type HTTP header should be okay
    """
    assert http_no_content_type_response.r.content_type is None
