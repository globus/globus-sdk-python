import pytest

import globus_sdk
from globus_sdk._testing import load_response


# TODO: add data for the success case and test it
@pytest.mark.xfail
def test_oauth2_userinfo():
    raise NotImplementedError


@pytest.mark.parametrize("casename", ("unauthorized", "forbidden"))
def test_oauth2_error_handling(client, casename):
    meta = load_response(client.oauth2_userinfo, case=casename).metadata

    with pytest.raises(globus_sdk.AuthAPIError) as excinfo:
        client.oauth2_userinfo()

    err = excinfo.value
    assert err.http_status == meta["http_status"]
    assert err.code == meta["code"]
    assert err.request_id == meta["error_id"]
