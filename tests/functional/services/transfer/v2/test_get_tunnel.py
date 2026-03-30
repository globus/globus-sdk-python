from globus_sdk.testing import get_last_request, load_response


def test_get_tunnel(client):
    meta = load_response(client.get_tunnel).metadata

    res = client.get_tunnel(meta["tunnel_id"])
    assert res.http_status == 200
    assert res["data"]["type"] == "Tunnel"
    assert res["data"]["id"] == meta["tunnel_id"]

    req = get_last_request()
    assert req.body is None
