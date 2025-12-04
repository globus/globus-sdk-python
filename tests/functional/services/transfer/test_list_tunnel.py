from globus_sdk.testing import get_last_request, load_response


def test_list_tunnel(client):
    load_response(client.list_tunnels)

    res = client.list_tunnels()
    assert res.http_status == 200
    assert len(res["data"]) == 2

    req = get_last_request()
    assert req.body is None
