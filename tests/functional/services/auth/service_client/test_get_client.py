from __future__ import annotations

import uuid

import pytest

from globus_sdk import GlobusSDKUsageError
from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "uuid_type",
    (str, uuid.UUID),
)
def test_get_client_by_id(
    service_client,
    uuid_type: type[str] | type[uuid.UUID],
):
    meta = load_response(service_client.get_client).metadata

    if uuid_type is str:
        res = service_client.get_client(client_id=meta["client_id"])
    else:
        res = service_client.get_client(client_id=uuid.UUID(meta["client_id"]))

    assert res["client"]["id"] == meta["client_id"]


def test_get_client_by_fqdn(
    service_client,
):
    meta = load_response(service_client.get_client, case="fqdn").metadata
    res = service_client.get_client(fqdn=meta["fqdn"])

    assert res["client"]["id"] == meta["client_id"]


def test_get_client_exactly_one_of_id_or_fqdn(
    service_client,
):
    with pytest.raises(GlobusSDKUsageError):
        service_client.get_client()

    with pytest.raises(GlobusSDKUsageError):
        service_client.get_client(
            client_id="1b72b72e-5251-454d-af67-0be35911d174",
            fqdn="globus.org",
        )
