from __future__ import annotations

import uuid

import pytest

from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "uuid_type",
    (str, uuid.UUID),
)
def test_get_project(
    service_client,
    uuid_type: type[str] | type[uuid.UUID],
):
    meta = load_response(service_client.get_project).metadata

    if uuid_type is str:
        res = service_client.get_project(meta["project_id"])
    else:
        res = service_client.get_project(uuid.UUID(meta["project_id"]))

    assert res["project"]["id"] == meta["project_id"]
