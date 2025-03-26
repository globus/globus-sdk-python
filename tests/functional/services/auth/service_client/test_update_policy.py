from __future__ import annotations

import pytest

from globus_sdk._testing import load_response


@pytest.mark.parametrize(
    "case_name",
    (
        "project_id_str",
        "project_id_uuid",
        "authentication_assurance_timeout",
        "required_mfa",
        "not_required_mfa",
        "display_name",
        "description",
        "no_domain_constrants_include",
        "empty_domain_constrants_include",
        "domain_constrants_include",
        "no_domain_constrants_exclude",
        "empty_domain_constrants_exclude",
        "domain_constrants_exclude",
    ),
)
def test_update_policy(
    service_client,
    case_name: str,
):
    meta = load_response(service_client.update_policy, case=case_name).metadata

    res = service_client.update_policy(**meta["args"])
    for k, v in meta["response"].items():
        assert res["policy"][k] == v
