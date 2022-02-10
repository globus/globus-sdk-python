import json

from globus_sdk import GCSRoleDocument
from tests.common import get_last_request, register_api_route_fixture_file


def test_get_role_list(client):
    register_api_route_fixture_file("gcs", "/roles", "role_list.json")
    res = client.get_role_list()

    assert len(list(res)) == 2
    # sanity check some fields
    assert res["DATA_TYPE"] == "result#1.0.0"
    for item in res:
        assert item["DATA_TYPE"] == "role#1.0.0"
        assert "id" in item
        assert item["id"] in ("{role_id_1}", "{role_id_2}")
        assert "principal" in item
        assert "role" in item


def test_get_role_list_params(client):
    """
    confirms include, collection_id, and arbitrary query_params arguments
    to get_role_list are assembled correctly
    """
    register_api_route_fixture_file("gcs", "/roles", "role_list.json")

    # no args
    res = client.get_role_list()
    assert res["code"] == "success"
    params = get_last_request().params
    assert params == {}

    # collection_id
    res = client.get_role_list(collection_id="{collection_id_1}")
    assert res["code"] == "success"
    params = get_last_request().params
    assert params == {"collection_id": "{collection_id_1}"}

    # include
    res = client.get_role_list(include="all_roles")
    assert res["code"] == "success"
    params = get_last_request().params
    assert params == {"include": "all_roles"}

    # query_params
    res = client.get_role_list(query_params={"foo": "bar"})
    assert res["code"] == "success"
    params = get_last_request().params
    assert params == {"foo": "bar"}

    # everything together
    res = client.get_role_list(
        collection_id="{collection_id_1}",
        include="all_roles",
        query_params={"foo": "bar"},
    )
    assert res["code"] == "success"
    params = get_last_request().params
    assert params == {
        "collection_id": "{collection_id_1}",
        "include": "all_roles",
        "foo": "bar",
    }


def test_create_role(client):
    register_api_route_fixture_file(
        "gcs", "/roles", "role_document.json", method="POST"
    )

    data = GCSRoleDocument(
        collection="{collection_id_1}",
        principal="urn:globus:auth:identity:{user_id_1}",
        role="owner",
    )
    res = client.create_role(data)
    assert res["id"] == "{role_id_1}"

    json_body = json.loads(get_last_request().body)

    assert json_body["collection"] in (None, "{collection_id_1}")
    assert json_body["principal"] == "urn:globus:auth:identity:{user_id_1}"
    assert json_body["role"] in ("owner", "administrator")


def test_get_role(client):
    register_api_route_fixture_file("gcs", "/roles/ROLE_ID", "role_document.json")
    res = client.get_role("ROLE_ID")
    assert res["DATA_TYPE"] == "role#1.0.0"
    assert res["id"] == "{role_id_1}"
    assert res["collection"] is None
    assert res["principal"] == "urn:globus:auth:identity:{user_id_1}"
    assert res["role"] == "owner"


def test_delete_role(client):
    register_api_route_fixture_file(
        "gcs", "/roles/ROLE_ID", "empty_success.json", method="DELETE"
    )
    res = client.delete_role("ROLE_ID")
    assert res["DATA_TYPE"] == "result#1.0.0"
    assert "detail" in res.data
    assert res.data["detail"] == "success"
