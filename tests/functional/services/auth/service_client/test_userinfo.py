import pytest

import globus_sdk
from globus_sdk.testing import load_response


# TODO: add data for the success case and test it
@pytest.mark.xfail
def test_userinfo():
    raise NotImplementedError


@pytest.mark.parametrize("casename", ("unauthorized", "forbidden"))
def test_userinfo_error_handling(service_client, casename):
    meta = load_response(service_client.oauth2_userinfo, case=casename).metadata

    with pytest.raises(globus_sdk.AuthAPIError) as excinfo:
        service_client.userinfo()

    err = excinfo.value
    assert err.http_status == meta["http_status"]
    assert err.code == meta["code"]
    assert err.request_id == meta["error_id"]


def test_oauth2_userinfo_warns(service_client):
    # TODO:
    # if the above success case is added, this test can be changed to use it
    # that would let us get rid of the try-except guard below
    load_response(service_client.oauth2_userinfo, case="unauthorized")

    with pytest.warns(globus_sdk.RemovedInV4Warning, match="Use `userinfo` instead."):
        try:
            service_client.oauth2_userinfo()
        except globus_sdk.AuthAPIError:
            pass
