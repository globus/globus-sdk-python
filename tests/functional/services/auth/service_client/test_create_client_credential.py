from __future__ import annotations

import uuid

import pytest

from globus_sdk.testing import load_response


@pytest.mark.parametrize("uuid_type", (str, uuid.UUID))
def test_create_credential(
    service_client,
    uuid_type: type[str] | type[uuid.UUID],
):
    meta = load_response(service_client.create_client_credential).metadata

    res = service_client.create_client_credential(
        meta["client_id"] if uuid_type is str else uuid.UUID(meta["client_id"]),
        meta["name"],
    )

    assert res["credential"]["id"] == meta["credential_id"]


def test_create_credential_set_name(
    service_client,
):
    meta = load_response(service_client.create_client_credential, case="name").metadata

    res = service_client.create_client_credential(meta["client_id"], meta["name"])

    assert res["credential"]["name"] == meta["name"]
