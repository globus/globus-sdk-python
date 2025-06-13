import json
import urllib.parse
import uuid

import pytest
import responses

import globus_sdk
from globus_sdk._missing import filter_missing
from globus_sdk._testing import get_last_request, load_response
from tests.common import register_api_route_fixture_file


@pytest.fixture
def search_client(no_retry_transport):
    class CustomSearchClient(globus_sdk.SearchClient):
        transport_class = no_retry_transport

    return CustomSearchClient()


def test_search_query_simple(search_client):
    meta = load_response(search_client.search).metadata

    res = search_client.search(meta["index_id"], q="foo")
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert data["gmeta"][0]["entries"][0]["content"]["foo"] == "bar"

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert parsed_qs == {"q": ["foo"]}


@pytest.mark.parametrize("query_doc", [{"q": "foo"}, {"q": "foo", "limit": 10}])
def test_search_post_query_simple(search_client, query_doc):
    meta = load_response(search_client.post_search).metadata

    res = search_client.post_search(meta["index_id"], query_doc)
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert data["gmeta"][0]["entries"][0]["content"]["foo"] == "bar"

    req = get_last_request()
    assert req.body is not None
    req_body = json.loads(req.body)
    assert req_body == dict(query_doc)


def test_search_post_query_with_legacy_helper(search_client):
    meta = load_response(search_client.post_search).metadata
    with pytest.warns(
        globus_sdk.RemovedInV4Warning, match="'SearchQuery' is deprecated"
    ):
        query_doc = globus_sdk.SearchQuery("foo")

    res = search_client.post_search(meta["index_id"], query_doc)
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert data["gmeta"][0]["entries"][0]["content"]["foo"] == "bar"

    req = get_last_request()
    assert req.body is not None
    req_body = json.loads(req.body)
    assert req_body == filter_missing(query_doc)


def test_search_post_query_simple_with_v1_helper(search_client):
    query_doc = globus_sdk.SearchQueryV1(q="foo")
    meta = load_response(search_client.post_search).metadata

    res = search_client.post_search(meta["index_id"], query_doc)
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert data["gmeta"][0]["entries"][0]["content"]["foo"] == "bar"

    req = get_last_request()
    assert req.body is not None
    req_body = json.loads(req.body)
    assert req_body == {"@version": "query#1.0.0", "q": "foo"}


def test_search_post_query_arg_overrides(search_client):
    meta = load_response(search_client.post_search).metadata

    query_doc = {"q": "foo", "limit": 10, "offset": 0}
    res = search_client.post_search(meta["index_id"], query_doc, limit=100, offset=150)
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert data["gmeta"][0]["entries"][0]["content"]["foo"] == "bar"

    req = get_last_request()
    assert req.body is not None
    req_body = json.loads(req.body)
    assert req_body != dict(query_doc)
    assert req_body["q"] == query_doc["q"]
    assert req_body["limit"] == 100
    assert req_body["offset"] == 150
    # important! these should be unchanged (no side-effects)
    assert query_doc["limit"] == 10
    assert query_doc["offset"] == 0


def test_search_post_query_arg_overrides_with_legacy_helper(search_client):
    meta = load_response(search_client.post_search).metadata
    with pytest.warns(
        globus_sdk.RemovedInV4Warning, match="'SearchQuery' is deprecated"
    ):
        query_doc = globus_sdk.SearchQuery("foo", limit=10, offset=0)

    res = search_client.post_search(meta["index_id"], query_doc, limit=100, offset=150)
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert data["gmeta"][0]["entries"][0]["content"]["foo"] == "bar"

    req = get_last_request()
    assert req.body is not None
    req_body = json.loads(req.body)
    assert req_body != dict(query_doc)
    assert req_body["q"] == query_doc["q"]
    assert req_body["limit"] == 100
    assert req_body["offset"] == 150
    # important! these should be unchanged (no side-effects)
    assert query_doc["limit"] == 10
    assert query_doc["offset"] == 0


@pytest.mark.parametrize(
    "query_doc",
    [
        {"q": "foo"},
        globus_sdk.SearchScrollQuery("foo"),
    ],
)
def test_search_paginated_scroll_query(search_client, query_doc):
    index_id = str(uuid.uuid1())
    register_api_route_fixture_file(
        "search",
        f"/v1/index/{index_id}/scroll",
        "scroll_result_1.json",
        method="POST",
        match=[responses.matchers.json_params_matcher({"q": "foo"})],
    )
    register_api_route_fixture_file(
        "search",
        f"/v1/index/{index_id}/scroll",
        "scroll_result_2.json",
        method="POST",
        match=[
            responses.matchers.json_params_matcher(
                {"q": "foo", "marker": "3d34900e3e4211ebb0a806b2af333354"}
            )
        ],
    )

    data = list(search_client.paginated.scroll(index_id, query_doc).items())
    assert len(responses.calls) == 2
    assert len(data) == 2

    assert isinstance(data[0], dict)
    assert data[0]["entries"][0]["content"]["foo"] == "bar"

    assert isinstance(data[1], dict)
    assert data[1]["entries"][0]["content"]["foo"] == "baz"

    # confirm that pagination was not side-effecting
    assert "marker" not in filter_missing(query_doc)
