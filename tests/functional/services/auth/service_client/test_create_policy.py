from __future__ import annotations

import pytest

from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "case_name",
    (
        "project_id_str",
        "project_id_uuid",
        "high_assurance",
        "not_high_assurance",
        "required_mfa",
        "authentication_assurance_timeout",
        "display_name",
        "description",
        "domain_constraints_include",
        "empty_domain_constraints_include",
        "no_domain_constraints_include",
        "domain_constraints_exclude",
        "empty_domain_constraints_exclude",
        "no_domain_constraints_exclude",
    ),
)
def test_create_policy(
    service_client,
    case_name: str,
):
    meta = load_response(service_client.create_policy, case=case_name).metadata

    res = service_client.create_policy(**meta["args"])
    for k, v in meta["response"].items():
        assert res["policy"][k] == v
