import json
import uuid

import pytest

from globus_sdk.testing import get_last_request, load_response


def test_get_endpoint(client):
    """
    Gets endpoint on fixture, validate results
    """
    meta = load_response(client.get_endpoint).metadata
    epid = meta["endpoint_id"]

    # load the endpoint document
    ep_doc = client.get_endpoint(epid)

    # check that the contents are basically OK
    assert ep_doc["DATA_TYPE"] == "endpoint"
    assert ep_doc["id"] == epid
    assert "display_name" in ep_doc


@pytest.mark.parametrize("epid_type", [uuid.UUID, str])
def test_update_endpoint(epid_type, client):
    meta = load_response(client.update_endpoint).metadata
    epid = meta["endpoint_id"]

    # NOTE: pass epid as UUID or str
    # requires that TransferClient correctly translates UUID
    update_data = {"display_name": "Updated Name", "description": "Updated description"}
    update_doc = client.update_endpoint(epid_type(epid), update_data)

    # make sure response is a successful update
    assert update_doc["DATA_TYPE"] == "result"
    assert update_doc["code"] == "Updated"
    assert update_doc["message"] == "Endpoint updated successfully"

    req = get_last_request()
    assert json.loads(req.body) == update_data
