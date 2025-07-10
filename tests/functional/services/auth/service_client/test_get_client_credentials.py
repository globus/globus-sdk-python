from __future__ import annotations

import uuid

import pytest

from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "uuid_type",
    (str, uuid.UUID),
)
def test_get_client_credentials(
    service_client,
    uuid_type: type[str] | type[uuid.UUID],
):
    meta = load_response(service_client.get_client_credentials).metadata

    if uuid_type is str:
        res = service_client.get_client_credentials(meta["client_id"])
    else:
        res = service_client.get_client_credentials(uuid.UUID(meta["client_id"]))

    assert {cred["id"] for cred in res["credentials"]} == {meta["credential_id"]}
