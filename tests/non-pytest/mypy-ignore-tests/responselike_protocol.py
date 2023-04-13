# validate that GlobusAPIError and GlobusHTTPResponse both satisfy the SDK's
# ResponseLike protocol

import sys
import typing as t

import requests

from globus_sdk import GlobusAPIError, GlobusHTTPResponse
from globus_sdk._types import ResponseLike

if sys.version_info < (3, 11):
    from typing_extensions import assert_type
else:
    from typing import assert_type

sample_response = requests.Response()


def get_length_of_response(r: ResponseLike) -> int:
    return len(r.binary_content)


# confirm this test function is well-declared
get_length_of_response("foo")  # type: ignore[arg-type]


# check an error object
err = GlobusAPIError(sample_response)
assert_type(err.http_status, int)
assert_type(err.http_reason, str)
assert_type(err.headers, t.Mapping[str, str])
assert_type(err.content_type, str | None)
assert_type(err.text, str)
assert_type(err.binary_content, bytes)
assert_type(get_length_of_response(err), int)


# check an HTTP response object
resp = GlobusHTTPResponse(sample_response)
assert_type(resp.http_status, int)
assert_type(resp.http_reason, str)
assert_type(resp.headers, t.Mapping[str, str])
assert_type(resp.content_type, str | None)
assert_type(resp.text, str)
assert_type(resp.binary_content, bytes)
assert_type(get_length_of_response(resp), int)
