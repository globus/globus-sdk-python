import uuid

zero_id = uuid.UUID(int=0)
zero_id_s = str(zero_id)


def test_manage_collections_scope_helper(client):
    sc = client.get_gcs_endpoint_scopes(zero_id)
    assert (
        str(sc.manage_collections)
        == f"urn:globus:auth:scope:{zero_id_s}:manage_collections"
    )
    # data_access is separated from endpoint scopes
    assert not hasattr(sc, "data_access")


def test_data_access_scope_helper(client):
    sc = client.get_gcs_collection_scopes(zero_id)
    assert (
        str(sc.data_access) == f"https://auth.globus.org/scopes/{zero_id_s}/data_access"
    )
    assert str(sc.https) == f"https://auth.globus.org/scopes/{zero_id_s}/https"
    # manage_collections is separated from collection scopes
    assert not hasattr(sc, "manage_collections")


def test_contains_scope_properties(client):
    ep_sc = client.get_gcs_endpoint_scopes(zero_id)
    assert ep_sc.manage_collections in list(ep_sc)

    collection_sc = client.get_gcs_collection_scopes(zero_id)
    assert collection_sc.data_access in list(collection_sc)
