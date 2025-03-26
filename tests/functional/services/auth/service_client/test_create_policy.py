from __future__ import annotations

import json

import pytest

from globus_sdk import exc
from globus_sdk._testing import get_last_request, load_response


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


def test_compatible_create_policy_usage_rejects_too_many_positionals(service_client):
    load_response(service_client.create_policy)
    with pytest.raises(
        TypeError,
        match=r"create_policy\(\) takes 5 positional arguments but 6 were given",
    ):
        service_client.create_policy(1, 2, 3, 4, 5, 6)


def test_valid_compatible_policy_usage_emits_warning(service_client):
    load_response(service_client.create_policy)
    with pytest.warns(
        exc.RemovedInV4Warning,
        match=r"'AuthClient\.create_policy' received positional arguments",
    ):
        service_client.create_policy(
            "my_project_id",
            True,
            101,
            display_name="my_display_name",
            description="my_description",
        )

    lastreq = get_last_request()
    sent_data = json.loads(lastreq.body)
    assert sent_data["policy"] == {
        "project_id": "my_project_id",
        "high_assurance": True,
        "authentication_assurance_timeout": 101,
        "display_name": "my_display_name",
        "description": "my_description",
    }


def test_policy_usage_warns_and_errors_when_argument_is_supplied_twice(service_client):
    with pytest.raises(
        TypeError,
        match="create_policy\\(\\) got multiple values for argument 'project_id'",
    ):
        with pytest.warns(
            exc.RemovedInV4Warning,
            match="'AuthClient.create_policy()' received positional arguments",
        ):
            service_client.create_policy("my_project_id", project_id="my_project_id2")
