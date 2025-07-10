from __future__ import annotations

import pytest

from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "case_name",
    (
        "name",
        "description",
        "scope_suffix",
        "no_required_domains",
        "required_domains",
        "no_dependent_scopes",
        "dependent_scopes",
        "advertised",
        "not_advertised",
        "allows_refresh_token",
        "disallows_refresh_token",
    ),
)
def test_update_scope(
    service_client,
    case_name: str,
):
    meta = load_response(service_client.update_scope, case=case_name).metadata

    res = service_client.update_scope(**meta["args"])
    for k, v in meta["response"].items():
        assert res["scope"][k] == v
