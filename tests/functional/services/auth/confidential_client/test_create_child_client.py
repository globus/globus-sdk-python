from __future__ import annotations

import pytest

from globus_sdk import GlobusSDKUsageError
from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "case_name",
    (
        "name",
        "public_client",
        "private_client",
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
def test_create_child_client_args(
    auth_client,
    case_name: str,
):
    meta = load_response(auth_client.create_child_client, case=case_name).metadata

    res = auth_client.create_child_client(**meta["args"])
    for k, v in meta["response"].items():
        assert res["client"][k] == v


def test_links_requirement(auth_client):
    """
    Verify that terms_and_conditions and privacy_policy must be used together.
    """
    with pytest.raises(GlobusSDKUsageError):
        auth_client.create_child_client(
            "FOO",
            visibility="public",
            terms_and_conditions="https://foo.net",
        )

    with pytest.raises(GlobusSDKUsageError):
        auth_client.create_child_client(
            "FOO",
            visibility="public",
            privacy_policy="https://foo.net",
        )


def test_public_client_and_client_type_requirement(auth_client):
    """
    Verify that exactly one of ``public_client` and ``client_type`` are expected.
    """
    # Neither public_client nor client_type
    with pytest.raises(GlobusSDKUsageError):
        auth_client.create_child_client(
            "FOO",
        )

    # Both public_client and client_type
    with pytest.raises(GlobusSDKUsageError):
        auth_client.create_child_client(
            "FOO",
            public_client=True,
            client_type="GCS",
        )
