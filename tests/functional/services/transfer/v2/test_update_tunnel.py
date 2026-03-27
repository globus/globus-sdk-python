import json

from globus_sdk.experimental import TunnelUpdateDocument
from globus_sdk.testing import get_last_request, load_response


def test_update_tunnel(client):
    meta = load_response(client.update_tunnel).metadata

    label = "New Name"
    update_doc = TunnelUpdateDocument(label=label)
    res = client.update_tunnel(meta["tunnel_id"], update_doc)
    assert res.http_status == 200
    assert res["data"]["type"] == "Tunnel"

    req = get_last_request()
    sent = json.loads(req.body)
    assert sent["data"]["attributes"]["label"] == label
