from __future__ import annotations

import pytest

from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "case_name",
    (
        "template_id_str",
        "template_id_uuid",
        "name",
    ),
)
def test_create_native_app_instance(
    auth_client,
    case_name: str,
):
    meta = load_response(
        auth_client.create_native_app_instance, case=case_name
    ).metadata

    res = auth_client.create_native_app_instance(**meta["args"])
    for k, v in meta["response"].items():
        assert res["client"][k] == v
