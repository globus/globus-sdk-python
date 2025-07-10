import pytest

import globus_sdk
from globus_sdk.testing import construct_error


def test_construct_error_defaults_to_base_error_class():
    err = construct_error(body="foo", http_status=400)
    assert isinstance(err, globus_sdk.GlobusAPIError)


@pytest.mark.parametrize(
    "error_class",
    (
        globus_sdk.SearchAPIError,
        globus_sdk.AuthAPIError,
        globus_sdk.TransferAPIError,
        globus_sdk.FlowsAPIError,
        globus_sdk.GCSAPIError,
    ),
)
def test_construct_error_can_be_customized_to_service_error_classes(error_class):
    err = construct_error(body="foo", http_status=400, error_class=error_class)
    assert isinstance(err, error_class)


def test_construct_error_defaults_to_json_for_dict_body():
    err = construct_error(body={"foo": "bar"}, http_status=400)
    assert err.text == '{"foo": "bar"}'
    assert err.headers == {"Content-Type": "application/json"}


@pytest.mark.parametrize(
    "body, add_params, expect_encoding, expect_text",
    (
        (b"foo-bar", {}, "utf-8", "foo-bar"),
        (b"foo-bar", {"response_encoding": "utf-8"}, "utf-8", "foo-bar"),
        (b"foo-bar", {"response_encoding": "latin-1"}, "latin-1", "foo-bar"),
        # this is invalid utf-8 (continuation byte),
        # but valid in latin-1 (e with acute accent)
        (b"\xe9", {"response_encoding": "latin-1"}, "latin-1", "é"),
    ),
)
def test_construct_error_allows_binary_content(
    body, add_params, expect_encoding, expect_text
):
    err = construct_error(body=body, http_status=400, **add_params)
    assert err.binary_content == body
    assert err.text == expect_text
    assert err._underlying_response.encoding == expect_encoding
