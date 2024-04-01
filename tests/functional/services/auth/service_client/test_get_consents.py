from globus_sdk._testing import load_response


def test_get_consents(service_client):
    meta = load_response(service_client.get_consents).metadata
    res = service_client.get_consents(meta["identity_id"])

    forest = res.to_forest()
    assert len(forest.nodes) == 2
    assert len(forest.trees) == 1
    tree = forest.trees[0]
    assert forest.trees[0].max_depth == 2
    assert tree.root.scope_name.endswith("transfer.api.globus.org:all")
    children = [tree.get_node(child_id) for child_id in tree.edges[tree.root.id]]
    assert len(children) == 1
    assert children[0].scope_name.endswith("data_access")
