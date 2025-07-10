from __future__ import annotations

import uuid

import pytest

from globus_sdk import GlobusSDKUsageError
from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "case_name",
    (
        "name",
        "publicly_visible",
        "not_publicly_visible",
        "redirect_uris",
        "links",
        "required_idp",
        "preselect_idp",
    ),
)
def test_update_client_args(
    service_client,
    case_name: str,
):
    meta = load_response(service_client.update_client, case=case_name).metadata

    res = service_client.update_client(**meta["args"])
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
