from globus_sdk.testing import get_last_request, load_response


def test_get_tunnel(client):
    meta = load_response(client.get_stream_access_point).metadata

    res = client.get_stream_access_point(meta["access_point_id"])
    assert res.http_status == 200
    assert res["data"]["type"] == "StreamAccessPoint"
    assert res["data"]["id"] == meta["access_point_id"]

    req = get_last_request()
    assert req.body is None
