import http
import sys
import typing as t

import pytest

from globus_sdk.testing import RegisteredResponse


@pytest.mark.skipif(
    sys.version_info < (3, 11), reason="test requires http.HTTPMethod (Python 3.11+)"
)
def test_registered_response_method_literal_type_is_correct():
    all_known_methods = [m.value for m in http.HTTPMethod]
    init_signature = t.get_type_hints(RegisteredResponse.__init__)

    method_arg_type = init_signature["method"]
    expected_method_arg_type = t.Literal[tuple(all_known_methods)]

    assert method_arg_type == expected_method_arg_type
