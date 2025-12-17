import json
import uuid

import pytest

from globus_sdk import exc
from globus_sdk.services.transfer import CreateTunnelData
from globus_sdk.testing import get_last_request, load_response


def test_create_tunnel(client):
    meta = load_response(client.create_tunnel).metadata

    submission_id = uuid.uuid4()
    data = CreateTunnelData(
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
    load_response(client.get_submission_id)

    data = CreateTunnelData(
        meta["initiator_ap"], meta["listener_ap"], label=meta["display_name"]
    )

    res = client.create_tunnel(data)
    assert res.http_status == 200

    req = get_last_request()
    sent = json.loads(req.body)
    assert sent["data"]["attributes"]["submission_id"] is not None


def test_create_tunnel_bad_input(client):
    data = {
        "relationships": {
            "listener": {
                "data": {
                    "type": "StreamAccessPoint",
                }
            },
            "initiator": {
                "data": {
                    "type": "StreamAccessPoint",
                }
            },
        }
    }

    with pytest.raises(exc.GlobusSDKUsageError):
        client.create_tunnel(data)
