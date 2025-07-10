from __future__ import annotations

import uuid

import pytest

from globus_sdk import GlobusSDKUsageError
from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "case_name",
    (
        "name",
        "public_client",
        "private_client",
        "project_id",
        "publicly_visible",
        "not_publicly_visible",
        "redirect_uris",
        "links",
        "required_idp",
        "preselect_idp",
        "client_type_confidential_client",
        "client_type_public_installed_client",
        "client_type_client_identity",
        "client_type_resource_server",
        "client_type_globus_connect_server",
        "client_type_hybrid_confidential_client_resource_server",
        "client_type_public_webapp_client",
    ),
)
def test_create_client_args(
    service_client,
    case_name: str,
):
    meta = load_response(service_client.create_client, case=case_name).metadata

    res = service_client.create_client(**meta["args"])
    for k, v in meta["response"].items():
        assert res["client"][k] == v


def test_links_requirement(service_client):
    """
    Verify that terms_and_conditions and privacy_policy must be used together.
    """
    with pytest.raises(GlobusSDKUsageError):
        service_client.create_client(
            "FOO",
            uuid.uuid1(),
            visibility="public",
            terms_and_conditions="https://foo.net",
        )

    with pytest.raises(GlobusSDKUsageError):
        service_client.create_client(
            "FOO",
            uuid.uuid1(),
            visibility="public",
            privacy_policy="https://foo.net",
        )


def test_public_client_and_client_type_requirement(service_client):
    """
    Verify that exactly one of ``public_client` and ``client_type`` are expected.
    """
    # Neither public_client nor client_type
    with pytest.raises(GlobusSDKUsageError):
        service_client.create_client(
            "FOO",
            uuid.uuid1(),
        )

    # Both public_client and client_type
    with pytest.raises(GlobusSDKUsageError):
        service_client.create_client(
            "FOO",
            uuid.uuid1(),
            public_client=True,
            client_type="GCS",
        )
