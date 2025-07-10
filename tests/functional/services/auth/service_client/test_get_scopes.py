import pytest

from globus_sdk import GlobusSDKUsageError
from globus_sdk.testing import load_response


def test_get_scopes(service_client):
    meta = load_response(service_client.get_scopes).metadata
    res = service_client.get_scopes()

    assert {scope["id"] for scope in res["scopes"]} == set(meta["scope_ids"])


def test_get_scopes_by_ids(service_client):
    meta = load_response(service_client.get_scopes, case="id").metadata
    res = service_client.get_scopes(ids=[meta["scope_id"]])

    assert res["scopes"][0]["id"] == meta["scope_id"]


def test_get_scopes_by_strings(service_client):
    meta = load_response(service_client.get_scopes, case="string").metadata
    res = service_client.get_scopes(scope_strings=[meta["scope_string"]])

    assert res["scopes"][0]["scope_string"] == meta["scope_string"]


def test_get_scopes_id_strings_mutually_exclusive(service_client):
    with pytest.raises(GlobusSDKUsageError):
        service_client.get_scopes(
            scope_strings=["foo"],
            ids=["18a8cd00-700a-4fcb-b6da-6efca558c369"],
        )
