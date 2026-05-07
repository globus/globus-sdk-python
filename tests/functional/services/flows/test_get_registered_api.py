import uuid

import pytest

from globus_sdk.testing import get_last_request, load_response


@pytest.mark.parametrize("use_uuid", [False, True])
def test_get_registered_api(flows_client, use_uuid):
    """Test get_registered_api with string ID and UUID ID"""
    loaded_response = load_response(flows_client.get_registered_api)
    _, meta = loaded_response.json, loaded_response.metadata

    registered_api_id_str = meta["registered_api_id"]
    registered_api_id = (
        uuid.UUID(registered_api_id_str) if use_uuid else registered_api_id_str
    )

    res = flows_client.get_registered_api(registered_api_id)

    assert res.http_status == 200
    assert res["id"] == registered_api_id_str
    assert res["name"] == meta["name"]

    req = get_last_request()
    assert req.body is None
    assert f"/registered_apis/{registered_api_id_str}" in req.url
