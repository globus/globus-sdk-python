from __future__ import annotations

import uuid

import pytest

from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "uuid_type",
    (str, uuid.UUID),
)
def test_delete_client(
    service_client,
    uuid_type: type[str] | type[uuid.UUID],
):
    meta = load_response(service_client.delete_client).metadata

    if uuid_type is str:
        res = service_client.delete_client(client_id=meta["client_id"])
    else:
        res = service_client.delete_client(client_id=uuid.UUID(meta["client_id"]))

    assert res["client"]["id"] == meta["client_id"]
