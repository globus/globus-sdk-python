from __future__ import annotations

import uuid

import pytest

from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "uuid_type",
    (str, uuid.UUID),
)
def test_get_policy(
    service_client,
    uuid_type: type[str] | type[uuid.UUID],
):
    meta = load_response(service_client.get_policy).metadata

    if uuid_type is str:
        res = service_client.get_policy(meta["policy_id"])
    else:
        res = service_client.get_policy(uuid.UUID(meta["policy_id"]))

    assert res["policy"]["id"] == meta["policy_id"]
