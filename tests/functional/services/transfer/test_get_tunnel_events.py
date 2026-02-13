from globus_sdk.testing import get_last_request, load_response


def test_get_tunnel(client):
    meta = load_response(client.get_tunnel_events).metadata
    res = client.get_tunnel_events(meta["tunnel_id"])
    assert res.http_status == 200
    assert res["data"][0]["type"] == "TunnelEvent"
    assert res["data"][1]["type"] == "TunnelEvent"

    req = get_last_request()
    assert req.body is None
