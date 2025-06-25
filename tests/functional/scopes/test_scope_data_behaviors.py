import uuid

import pytest

from globus_sdk.scopes import (
    AuthScopes,
    ComputeScopes,
    FlowsScopes,
    GCSCollectionScopes,
    GCSEndpointScopes,
    GroupsScopes,
    NexusScopes,
    Scope,
    SearchScopes,
    SpecificFlowScopes,
    TimersScopes,
    TransferScopes,
)


@pytest.mark.parametrize(
    "collection, expect_resource_server",
    (
        (AuthScopes, "auth.globus.org"),
        (ComputeScopes, "funcx_service"),
        (FlowsScopes, "flows.globus.org"),
        (GroupsScopes, "groups.api.globus.org"),
        (NexusScopes, "nexus.api.globus.org"),
        (SearchScopes, "search.api.globus.org"),
        (TimersScopes, "524230d7-ea86-4a52-8312-86065a9e0417"),
        (TransferScopes, "transfer.api.globus.org"),
    ),
)
def test_static_resource_server_attributes(collection, expect_resource_server):
    assert collection.resource_server == expect_resource_server


@pytest.mark.parametrize(
    "collection_cls", (GCSEndpointScopes, GCSCollectionScopes, SpecificFlowScopes)
)
def test_dynamic_resource_server_attributes(collection_cls):
    some_id = str(uuid.UUID(int=1))
    coll = collection_cls(some_id)
    assert coll.resource_server == some_id


def test_oidc_scope_formatting():
    assert str(AuthScopes.openid) == "openid"
    assert str(AuthScopes.email) == "email"
    assert str(AuthScopes.profile) == "profile"


def test_non_oidc_auth_scope_formatting():
    non_oidc_scopes = set(AuthScopes).difference(
        (AuthScopes.openid, AuthScopes.email, AuthScopes.profile)
    )

    assert len(non_oidc_scopes) > 0
    assert all(isinstance(x, Scope) for x in non_oidc_scopes)

    scope_strs = [str(s) for s in non_oidc_scopes]
    assert all(
        s.startswith("urn:globus:auth:scope:auth.globus.org:") for s in scope_strs
    )
