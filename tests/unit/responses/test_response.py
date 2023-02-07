import json
import re
from collections import namedtuple
from unittest import mock

import pytest
import requests

from globus_sdk.response import ArrayResponse, GlobusHTTPResponse, IterableResponse

_TestResponse = namedtuple("_TestResponse", ("data", "r"))


def _response(data=None, encoding="utf-8", headers=None, status: int = 200):
    r = requests.Response()

    is_json = isinstance(data, (dict, list))

    datastr = json.dumps(data) if is_json else data
    if datastr is not None:
        if isinstance(datastr, str):
            r._content = datastr.encode("utf-8")
            r.encoding = "utf-8"
        else:
            r._content = datastr
            r.encoding = "ISO-8559-1"

    if headers:
        r.headers.update(headers)
    elif is_json:
        r.headers["Content-Type"] = "application/json"

    r.status_code = status

    r.reason = {200: "OK", 404: "Not Found"}.get(status, "Unknown")

    return r


def _mk_json_response(data):
    json_response = _response(data)
    return _TestResponse(data, GlobusHTTPResponse(json_response, client=mock.Mock()))


@pytest.fixture
def dict_response():
    return _mk_json_response({"label1": "value1", "label2": "value2"})


@pytest.fixture
def list_response():
    return _mk_json_response(["value1", "value2", "value3"])


@pytest.fixture
def http_no_content_type_response():
    res = _response()
    assert "Content-Type" not in res.headers
    return _TestResponse(None, GlobusHTTPResponse(res, client=mock.Mock()))


@pytest.fixture
def malformed_http_response():
    malformed_response = _response(b"{", headers={"Content-Type": "application/json"})
    return _TestResponse(
        "{", GlobusHTTPResponse(malformed_response, client=mock.Mock())
    )


@pytest.fixture
def text_http_response():
    text_data = "text data"
    text_response = _response(
        text_data, encoding="utf-8", headers={"Content-Type": "text/plain"}
    )
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


def test_text_response_repr_and_str_contain_raw_data():
    expect_text = """pu-erh is a distinctive aged tea primarily produced in Yunnan

    depending on the tea used and how it is aged, it can be bright, floral, and fruity
    or it can take on mushroomy, fermented, and malty notes
    """
    raw = _response(
        expect_text, encoding="utf-8", headers={"Content-Type": "text/plain"}
    )
    res = GlobusHTTPResponse(raw, client=mock.Mock())

    assert expect_text in repr(res)
    assert expect_text in str(res)


def test_getitem(dict_response, list_response):
    """
    Confirms that values can be accessed from the GlobusResponse
    """
    # str indexing
    for key in dict_response.data:
        assert dict_response.r[key] == dict_response.data[key]
    # int indexing
    for i in range(len(list_response.data)):
        assert list_response.r[i] == list_response.data[i]
    # slice indexing
    assert list_response.r[:-1] == list_response.data[:-1]


def test_contains(dict_response, list_response, text_http_response):
    """
    Confirms that individual values are seen in the GlobusResponse
    """
    for item in dict_response.data:
        assert item in dict_response.r
    assert "nonexistent" not in dict_response.r

    for item in list_response.data:
        assert item in list_response.r
    assert "nonexistent" not in list_response.r

    assert "foo" not in text_http_response.r


def test_bool(dict_response, list_response):
    assert bool(dict_response) is True
    assert bool(list_response) is True

    empty_dict, empty_list = _mk_json_response({}), _mk_json_response([])
    assert bool(empty_dict.r) is False
    assert bool(empty_list.r) is False

    null = _mk_json_response(None)
    assert bool(null.r) is False


def test_len_array(list_response):
    array = ArrayResponse(list_response.r)
    assert len(array) == len(list_response.data)

    empty_list = _mk_json_response([])
    empty_array = ArrayResponse(empty_list.r)
    assert len(empty_list.data) == 0
    assert len(empty_array) == 0


def test_len_array_bad_data(dict_response):
    null_array = ArrayResponse(_mk_json_response(None).r)
    with pytest.raises(
        TypeError,
        match=re.escape(
            "Cannot take len() on ArrayResponse data when type is 'NoneType'"
        ),
    ):
        len(null_array)

    dict_array = ArrayResponse(dict_response.r)
    with pytest.raises(
        TypeError,
        match=re.escape("Cannot take len() on ArrayResponse data when type is 'dict'"),
    ):
        len(dict_array)


def test_iter_array_bad_data(dict_response):
    null_array = ArrayResponse(_mk_json_response(None).r)
    with pytest.raises(
        TypeError,
        match=re.escape("Cannot iterate on ArrayResponse data when type is 'NoneType'"),
    ):
        list(null_array)

    dict_array = ArrayResponse(dict_response.r)
    with pytest.raises(
        TypeError,
        match=re.escape("Cannot iterate on ArrayResponse data when type is 'dict'"),
    ):
        list(dict_array)


def test_get(dict_response, list_response, text_http_response):
    """
    Gets individual values from dict response, confirms results
    Confirms list response correctly fails as non indexable
    """
    for item in dict_response.data:
        assert dict_response.r.get(item) == dict_response.data.get(item)

    assert list_response.r.get("value1") is None
    assert list_response.r.get("value1", "foo") == "foo"

    assert text_http_response.r.get("foo") is None
    assert text_http_response.r.get("foo", default="bar") == "bar"


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


def test_client_required_with_requests_response():
    r = _response({"foo": 1})
    GlobusHTTPResponse(r, client=mock.Mock())  # ok
    with pytest.raises(ValueError):
        GlobusHTTPResponse(r)  # not ok


def test_client_forbidden_when_wrapping():
    r = _response({"foo": 1})
    to_wrap = GlobusHTTPResponse(r, client=mock.Mock())

    GlobusHTTPResponse(to_wrap)  # ok
    with pytest.raises(ValueError):
        GlobusHTTPResponse(to_wrap, client=mock.Mock())  # not ok


def test_value_error_indexing_on_non_json_data():
    r = _response(b"foo: bar, baz: buzz")
    res = GlobusHTTPResponse(r, client=mock.Mock())

    with pytest.raises(ValueError):
        res["foo"]


def test_cannot_construct_base_iterable_response():
    r = _response(b"foo: bar, baz: buzz")
    with pytest.raises(TypeError):
        IterableResponse(r, client=mock.Mock())


def test_iterable_response_using_iter_key():
    class MyIterableResponse(IterableResponse):
        default_iter_key = "default_iter"

    raw = _response({"default_iter": [0, 1], "other_iter": [3, 4]})

    default = MyIterableResponse(raw, client=mock.Mock())
    assert list(default) == [0, 1]

    withkey = MyIterableResponse(raw, client=mock.Mock(), iter_key="other_iter")
    assert list(withkey) == [3, 4]


def test_iterable_response_errors_on_non_dict_data(list_response):
    class MyIterableResponse(IterableResponse):
        default_iter_key = "default_iter"

    list_iterable = MyIterableResponse(list_response.r)
    null_iterable = MyIterableResponse(_mk_json_response(None).r)

    with pytest.raises(
        TypeError,
        match=re.escape("Cannot iterate on IterableResponse data when type is 'list'"),
    ):
        list(list_iterable)

    with pytest.raises(
        TypeError,
        match=re.escape(
            "Cannot iterate on IterableResponse data when type is 'NoneType'"
        ),
    ):
        list(null_iterable)


def test_can_iter_array_response(list_response):
    arr = ArrayResponse(list_response.r)
    # sorted/reversed are just example stdlib functions which use iter
    assert sorted(arr) == sorted(list_response.data)
    assert list(reversed(arr)) == list(reversed(list_response.data))


def test_http_status_code_on_response():
    r1 = _response(status=404)
    assert r1.status_code == 404

    r2 = GlobusHTTPResponse(r1, client=mock.Mock())  # handle a Response object
    assert r2.http_status == 404

    r3 = GlobusHTTPResponse(r2)  # wrap another response
    assert r3.http_status == 404


def test_http_reason_on_response():
    r1 = _response(status=404)
    r2 = GlobusHTTPResponse(r1, client=mock.Mock())  # handle a Response object
    r3 = GlobusHTTPResponse(r2)  # wrap another response
    assert r1.reason == "Not Found"
    assert r2.http_reason == "Not Found"
    assert r3.http_reason == "Not Found"

    r4 = _response(status=200)
    r5 = GlobusHTTPResponse(r4, client=mock.Mock())  # handle a Response object
    r6 = GlobusHTTPResponse(r5)  # wrap another response
    assert r4.reason == "OK"
    assert r5.http_reason == "OK"
    assert r6.http_reason == "OK"


def test_http_headers_from_response():
    r1 = _response(headers={"Content-Length": "5"})
    assert r1.headers["content-length"] == "5"

    r2 = GlobusHTTPResponse(r1, client=mock.Mock())  # handle a Response object
    assert r2.headers["content-length"] == "5"

    r3 = GlobusHTTPResponse(r2)  # wrap another response
    assert r3.headers["content-length"] == "5"
