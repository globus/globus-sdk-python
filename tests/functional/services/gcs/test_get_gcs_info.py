from globus_sdk._testing import get_last_request, load_response
from globus_sdk.authorizers import AccessTokenAuthorizer


def test_get_gcs_info(client):
    meta = load_response(client.get_gcs_info).metadata
    endpoint_client_id = meta["endpoint_client_id"]

    # set an authorizer
    client.authorizer = AccessTokenAuthorizer("access_token")

    res = client.get_gcs_info()
    assert res["endpoint_id"] == endpoint_client_id
    assert res["client_id"] == endpoint_client_id

    # confirm request was unauthenticated despite client having an authorizer
    req = get_last_request()
    assert "Authorization" not in req.headers
