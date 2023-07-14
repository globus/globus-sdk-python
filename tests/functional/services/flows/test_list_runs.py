import pytest

from globus_sdk._testing import load_response


def test_list_runs_simple(flows_client):
    meta = load_response(flows_client.list_runs).metadata

    res = flows_client.list_runs()
    assert res.http_status == 200

    # dict-like indexing
    assert meta["first_run_id"] == res["runs"][0]["run_id"]
    # list conversion (using __iter__) and indexing
    assert meta["first_run_id"] == list(res)[0]["run_id"]


@pytest.mark.parametrize("by_pages", [True, False])
def test_list_flows_paginated(flows_client, by_pages):
    meta = load_response(flows_client.list_runs, case="paginated").metadata
    total_items = meta["total_items"]
    num_pages = meta["num_pages"]
    expect_markers = meta["expect_markers"]

    res = flows_client.paginated.list_runs()
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
