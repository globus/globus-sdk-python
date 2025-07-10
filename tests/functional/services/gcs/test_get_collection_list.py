import pytest

from globus_sdk import MISSING, GCSAPIError
from globus_sdk.testing import get_last_request, load_response


def test_get_collection_list(client):
    meta = load_response(client.get_collection_list).metadata
    res = client.get_collection_list()

    # check the results against response metadata to ensure integrity and that
    # response parsing works
    assert len(list(res)) == len(meta["collection_ids"])
    assert res["DATA_TYPE"] == "result#1.0.0"
    for index, item in enumerate(res):
        assert item["DATA_TYPE"] == "collection#1.0.0"
        assert item["id"] == meta["collection_ids"][index]
        assert item["storage_gateway_id"] == meta["gateway_ids"][index]
        assert item["display_name"] == meta["display_names"][index]


@pytest.mark.parametrize(
    "include_param, expected",
    (
        (MISSING, None),
        ("foo", "foo"),
        ("foo,bar", "foo,bar"),
        (("foo", "bar"), "foo,bar"),
    ),
)
def test_get_collection_list_include_param(client, include_param, expected):
    load_response(client.get_collection_list)
    client.get_collection_list(include=include_param)
    req = get_last_request()
    if include_param is not MISSING:
        assert "include" in req.params
        assert req.params["include"] == expected
    else:
        assert "include" not in req.params


def test_get_collection_list_mapped_collection_id_param(client):
    load_response(client.get_collection_list)
    client.get_collection_list(mapped_collection_id="MAPPED_COLLECTION")
    assert get_last_request().params.get("mapped_collection_id") == "MAPPED_COLLECTION"


@pytest.mark.parametrize(
    "filter_param, expected",
    (
        (["mapped_collections", "created_by_me"], "mapped_collections,created_by_me"),
        ("created_by_me", "created_by_me"),
    ),
)
def test_get_collection_list_filter_param(client, filter_param, expected):
    load_response(client.get_collection_list)
    client.get_collection_list(filter=filter_param)
    assert get_last_request().params.get("filter") == expected


def test_error_parsing_forbidden(client):
    """
    This test is more focused on error parsing than it is on the actual collection list
    call.
    """
    load_response(client.get_collection_list, case="forbidden")
    with pytest.raises(GCSAPIError) as excinfo:
        client.get_collection_list()

    err = excinfo.value
    assert err.detail is None
    assert err.detail_data_type is None
    assert err.message.startswith("Could not list collections")
    assert err.code == "permission_denied"
