import pytest

import globus_sdk
from globus_sdk.testing import RegisteredResponse, load_response


def test_oauth2_validate_token_emits_deprecation_warning():
    nc = globus_sdk.NativeAppAuthClient("dummy_client_id")
    load_response(
        RegisteredResponse(
            service="auth",
            path="/v2/oauth2/token/validate",
            method="POST",
            json={"foo": "bar"},
        )
    )
    with pytest.warns(globus_sdk.RemovedInV4Warning):
        nc.oauth2_validate_token("dummy_token")
