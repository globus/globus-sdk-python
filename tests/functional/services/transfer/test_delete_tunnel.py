from globus_sdk.testing import get_last_request, load_response


def test_delete_tunnel(client):
    meta = load_response(client.delete_tunnel).metadata

    res = client.delete_tunnel(meta["tunnel_id"])
    assert res.http_status == 200

    req = get_last_request()
    assert req.body is None
