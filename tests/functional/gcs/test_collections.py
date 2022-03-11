import pytest

from globus_sdk import GCSAPIError, GuestCollectionDocument, MappedCollectionDocument
from globus_sdk._testing import get_last_request
from tests.common import register_api_route_fixture_file


def test_get_collection_list(client):
    register_api_route_fixture_file("gcs", "/collections", "collection_list.json")
    res = client.get_collection_list()

    assert len(list(res)) == 2
    # sanity check some fields
    assert res["DATA_TYPE"] == "result#1.0.0"
    for item in res:
        assert item["DATA_TYPE"] == "collection#1.0.0"
        assert "id" in item
        assert item["id"] in ("{collection_id_1}", "{collection_id_2}")
        assert "display_name" in item


def test_get_collection_list_include_param(client):
    register_api_route_fixture_file("gcs", "/collections", "collection_list.json")

    client.get_collection_list()
    req = get_last_request()
    assert "include" not in req.params

    client.get_collection_list(include="foo")
    req = get_last_request()
    assert "include" in req.params
    assert req.params["include"] == "foo"

    client.get_collection_list(include="foo,bar")
    req = get_last_request()
    assert "include" in req.params
    assert req.params["include"] == "foo,bar"

    client.get_collection_list(include=("foo", "bar"))
    req = get_last_request()
    assert "include" in req.params
    assert req.params["include"] == "foo,bar"

    client.get_collection_list(mapped_collection_id="MAPPED_COLLECTION")
    assert get_last_request().params.get("mapped_collection_id") == "MAPPED_COLLECTION"

    filters = ["mapped_collections", "created_by_me"]
    client.get_collection_list(filter=filters)
    assert get_last_request().params.get("filter") == ",".join(filters)

    client.get_collection_list(filter="created_by_me")
    assert get_last_request().params.get("filter") == "created_by_me"


def test_error_parsing_forbidden(client):
    register_api_route_fixture_file(
        "gcs", "/collections", "forbidden_error_data.json", status=403
    )
    with pytest.raises(GCSAPIError) as excinfo:
        client.get_collection_list()

    err = excinfo.value
    assert err.detail is None
    assert err.detail_data_type is None
    assert err.message.startswith("Could not list collections")
    assert err.code == "permission_denied"


def test_get_collection(client):
    register_api_route_fixture_file(
        "gcs", "/collections/COLLECTION_ID", "get_collection/normal.json"
    )
    res = client.get_collection("COLLECTION_ID")
    assert res["DATA_TYPE"] == "collection#1.0.0"
    assert res.full_data["DATA_TYPE"] == "result#1.0.0"
    assert "detail" in res.full_data
    assert "data" in res.full_data
    assert res.full_data["detail"] == "success"
    assert "detail" not in res.data
    assert res["display_name"] == "Happy Fun Collection Name"


def test_get_collection_flat(client):
    register_api_route_fixture_file(
        "gcs", "/collections/COLLECTION_ID", "get_collection/unexpectedly_flat.json"
    )
    res = client.get_collection("COLLECTION_ID")
    assert res["DATA_TYPE"] == "collection#1.0.0"
    assert res.full_data["DATA_TYPE"] == "collection#1.0.0"
    assert "detail" not in res.full_data
    assert "data" not in res.full_data
    assert res["display_name"] == "Happy Fun Collection Name"


def test_get_collection_bad_version(client):
    register_api_route_fixture_file(
        "gcs", "/collections/COLLECTION_ID", "get_collection/bad_version.json"
    )
    res = client.get_collection("COLLECTION_ID")
    assert res["DATA_TYPE"] == "result#1.0.0"
    assert res.full_data["DATA_TYPE"] == "result#1.0.0"
    assert "detail" in res.full_data
    assert "data" in res.full_data
    assert res.full_data["detail"] == "success"
    assert "detail" in res.data
    assert "foo" not in res.data
    for x in res.full_data["data"]:
        assert "foo" in x


def test_get_collection_includes_sideloaded_data(client):
    register_api_route_fixture_file(
        "gcs", "/collections/COLLECTION_ID", "get_collection/includes_other.json"
    )
    res = client.get_collection("COLLECTION_ID")
    assert res["DATA_TYPE"] == "collection#1.0.0"
    assert res.full_data["DATA_TYPE"] == "result#1.0.0"
    assert "detail" in res.full_data
    assert "data" in res.full_data
    assert res.full_data["detail"] == "success"
    assert "detail" not in res.data
    assert res["display_name"] == "Happy Fun Collection Name"


def test_get_collection_invalid_datatype_type(client):
    register_api_route_fixture_file(
        "gcs", "/collections/COLLECTION_ID", "get_collection/invalid_datatype_type.json"
    )
    res = client.get_collection("COLLECTION_ID")
    assert res["DATA_TYPE"] == "result#1.0.0"
    assert res.full_data["DATA_TYPE"] == "result#1.0.0"
    assert "detail" in res.full_data
    assert "detail" in res.data
    assert "data" in res.full_data
    assert res.full_data["detail"] == "success"


def test_delete_collection(client):
    register_api_route_fixture_file(
        "gcs", "/collections/COLLECTION_ID", "empty_success.json", method="DELETE"
    )
    res = client.delete_collection("COLLECTION_ID")
    assert res["DATA_TYPE"] == "result#1.0.0"
    assert "detail" in res.data
    assert res.data["detail"] == "success"


def test_create_mapped_collection(client):
    register_api_route_fixture_file(
        "gcs", "/collections", "create_collection.json", method="POST"
    )
    collection = MappedCollectionDocument(
        domain_name="i-f3c83.123.globus.org",
        display_name="Project Foo Research Data",
        identity_id="c8b7ab5c-595c-43c9-8e43-9e8a3debfe4c",
        storage_gateway_id="fc1f3ba0-1fa4-42b2-8bb3-53983774fa5f",
        collection_base_path="/",
        default_directory="/projects",
        public=True,
        force_encryption=False,
        disable_verify=False,
        organization="University of Example",
        department="Data Science",
        keywords=["Project Foo", "Data Intensive Science"],
        description='Information related to the "Foo" project.',
        contact_email="project-foo@example.edu",
        contact_info="+1 (555) 555-1234",
        info_link="https://project-foo.example.edu/info",
        policies={"DATA_TYPE": "blackpearl_collection_policies#1.0.0"},
        allow_guest_collections=True,
        sharing_restrict_paths={
            "DATA_TYPE": "path_restrictions#1.0.0",
            "read": ["/public"],
            "read_write": ["/home", "/projects"],
            "none": ["/private"],
        },
    )
    res = client.create_collection(collection)
    assert res["DATA_TYPE"] == "collection#1.0.0"
    assert res["display_name"] == "Project Foo Research Data"


def test_update_guest_collection(client):
    register_api_route_fixture_file(
        "gcs", "/collections/COLLECTION_ID", "update_collection.json", method="PATCH"
    )
    collection = GuestCollectionDocument(display_name="Project Foo Research Data")
    res = client.update_collection("COLLECTION_ID", collection)
    assert res["DATA_TYPE"] == "collection#1.0.0"
    assert res["display_name"] == "Project Foo Research Data"
