import urllib.parse

import pytest

from globus_sdk._testing import get_last_request, load_response


def test_create_flow(flows_client):
    metadata = load_response(flows_client.create_flow).metadata

    resp = flows_client.create_flow(**metadata["params"])
    assert resp.data["title"] == "Multi Step Transfer"


def test_get_flow(flows_client):
    meta = load_response(flows_client.get_flow).metadata
    resp = flows_client.get_flow(meta["flow_id"])
    assert resp.data["title"] == meta["title"]


def test_update_flow(flows_client):
    meta = load_response(flows_client.update_flow).metadata
    resp = flows_client.update_flow(meta["flow_id"], **meta["params"])
    for k, v in meta["params"].items():
        assert k in resp
        assert resp[k] == v


def test_delete_flow(flows_client):
    metadata = load_response(flows_client.delete_flow).metadata

    resp = flows_client.delete_flow(metadata["flow_id"])
    assert resp.data["title"] == "Multi Step Transfer"
    assert resp.data["DELETED"] is True


@pytest.mark.parametrize("filter_fulltext", [None, "foo"])
@pytest.mark.parametrize("filter_role", [None, "bar"])
@pytest.mark.parametrize("orderby", [None, "created_at ASC"])
def test_list_flows_simple(flows_client, filter_fulltext, filter_role, orderby):
    meta = load_response(flows_client.list_flows).metadata

    add_kwargs = {}
    if filter_fulltext:
        add_kwargs["filter_fulltext"] = filter_fulltext
    if filter_role:
        add_kwargs["filter_role"] = filter_role
    if orderby:
        add_kwargs["orderby"] = orderby

    res = flows_client.list_flows(**add_kwargs)
    assert res.http_status == 200
    # dict-like indexing
    assert meta["first_flow_id"] == res["flows"][0]["id"]
    # list conversion (using __iter__) and indexing
    assert meta["first_flow_id"] == list(res)[0]["id"]

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    expect_query_params = {
        k: [v]
        for k, v in (
            ("filter_fulltext", filter_fulltext),
            ("filter_role", filter_role),
            ("orderby", orderby),
        )
        if v is not None
    }
    assert parsed_qs == expect_query_params


@pytest.mark.parametrize("by_pages", [True, False])
def test_list_flows_paginated(flows_client, by_pages):
    meta = load_response(flows_client.list_flows, case="paginated").metadata
    total_items = meta["total_items"]
    num_pages = meta["num_pages"]
    expect_markers = meta["expect_markers"]

    res = flows_client.paginated.list_flows()
    if by_pages:
        pages = list(res)
        assert len(pages) == num_pages
        for i, page in enumerate(pages):
            assert page["marker"] == expect_markers[i]
            if i < num_pages - 1:
                assert page["has_next_page"] is True
            else:
                assert page["has_next_page"] is False
    else:
        items = list(res.items())
        assert len(items) == total_items
