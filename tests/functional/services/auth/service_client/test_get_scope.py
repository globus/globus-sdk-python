from __future__ import annotations

import uuid

import pytest

from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "uuid_type",
    (str, uuid.UUID),
)
def test_get_scope(
    service_client,
    uuid_type: type[str] | type[uuid.UUID],
):
    meta = load_response(service_client.get_scope).metadata

    if uuid_type is str:
        res = service_client.get_scope(scope_id=meta["scope_id"])
    else:
        res = service_client.get_scope(scope_id=uuid.UUID(meta["scope_id"]))

    assert res["scope"]["id"] == meta["scope_id"]
