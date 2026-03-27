import json
import uuid

from globus_sdk.experimental import TunnelCreateDocument
from globus_sdk.testing import get_last_request, load_response


def test_create_tunnel(client):
    meta = load_response(client.create_tunnel).metadata

    submission_id = uuid.uuid4()
    data = TunnelCreateDocument(
        meta["initiator_ap"],
        meta["listener_ap"],
        submission_id=submission_id,
        label=meta["display_name"],
    )

    res = client.create_tunnel(data)
    assert res.http_status == 200
    assert res["data"]["type"] == "Tunnel"

    req = get_last_request()
    sent = json.loads(req.body)
    assert (
        sent["data"]["relationships"]["initiator"]["data"]["id"] == meta["initiator_ap"]
    )
    assert (
        sent["data"]["relationships"]["listener"]["data"]["id"] == meta["listener_ap"]
    )
    assert sent["data"]["attributes"]["submission_id"] == str(submission_id)
    assert sent["data"]["attributes"]["label"] == meta["display_name"]


def test_create_tunnel_no_submission(client):
    meta = load_response(client.create_tunnel).metadata

    data = TunnelCreateDocument(
        meta["initiator_ap"], meta["listener_ap"], label=meta["display_name"]
    )

    # confirm TunnelCreateDocument auto-generated a submission_id
    generated_uuid = data["data"]["attributes"]["submission_id"]
    assert isinstance(generated_uuid, uuid.UUID)

    res = client.create_tunnel(data)
    assert res.http_status == 200

    req = get_last_request()
    sent = json.loads(req.body)
    assert sent["data"]["attributes"]["submission_id"] == str(generated_uuid)
