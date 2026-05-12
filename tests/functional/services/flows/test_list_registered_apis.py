import urllib.parse

import pytest

from globus_sdk import MISSING
from globus_sdk.testing import get_last_request, load_response


@pytest.mark.parametrize("filter_roles", [MISSING, "owner"])
@pytest.mark.parametrize("orderby", [MISSING, "name ASC"])
def test_list_registered_apis_simple(flows_client, filter_roles, orderby):
    meta = load_response(flows_client.list_registered_apis).metadata

    add_kwargs = {}
    if filter_roles is not MISSING:
        add_kwargs["filter_roles"] = filter_roles
    if orderby is not MISSING:
        add_kwargs["orderby"] = orderby

    res = flows_client.list_registered_apis(**add_kwargs)

    assert res.http_status == 200
    # dict-like indexing
    assert meta["first_registered_api_id"] == res["registered_apis"][0]["id"]
    # list conversion (using __iter__) and indexing
    assert meta["first_registered_api_id"] == list(res)[0]["id"]

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    expect_query_params = {
        k: [v]
        for k, v in (
            ("filter_roles", filter_roles),
            ("orderby", orderby),
        )
        if v is not MISSING
    }
    assert parsed_qs == expect_query_params


@pytest.mark.parametrize("by_pages", [True, False])
def test_list_registered_apis_paginated(flows_client, by_pages):
    meta = load_response(flows_client.list_registered_apis, case="paginated").metadata
    total_items = meta["total_items"]
    num_pages = meta["num_pages"]
    expect_markers = meta["expect_markers"]

    res = flows_client.paginated.list_registered_apis()
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
