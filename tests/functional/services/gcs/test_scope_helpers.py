import uuid

zero_id = uuid.UUID(int=0)
zero_id_s = str(zero_id)


def test_manage_collections_scope_helper(client):
    sb = client.get_gcs_endpoint_scopes(zero_id)
    assert (
        sb.manage_collections == f"urn:globus:auth:scope:{zero_id_s}:manage_collections"
    )
    # data_access is separated from endpoint scopes
    assert not hasattr(sb, "data_access")


def test_data_access_scope_helper(client):
    sb = client.get_gcs_collection_scopes(zero_id)
    assert sb.data_access == f"https://auth.globus.org/scopes/{zero_id_s}/data_access"
    assert sb.https == f"https://auth.globus.org/scopes/{zero_id_s}/https"
    # manage_collections is separated from collection scopes
    assert not hasattr(sb, "manage_collections")


def test_str_contains_scope_properties(client):
    ep_sb = client.get_gcs_endpoint_scopes(zero_id)

    assert "manage_collections" in str(ep_sb)
    assert ep_sb.manage_collections in str(ep_sb)

    collection_sb = client.get_gcs_collection_scopes(zero_id)

    assert "data_access" in str(collection_sb)
    assert collection_sb.data_access in str(collection_sb)
