import uuid

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
def test_list_runs_paginated(flows_client, by_pages):
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


@pytest.mark.parametrize("pass_as_uuids", [True, False])
def test_list_runs_filter_flow_id(flows_client, pass_as_uuids):
    meta = load_response(flows_client.list_runs, case="filter_flow_id").metadata
    # sanity check that the underlying test data hasn't changed too much
    assert len(meta["by_flow_id"]) == 2
    flow_id_one, flow_id_two = tuple(meta["by_flow_id"].keys())
    if pass_as_uuids:
        flow_id_one = uuid.UUID(flow_id_one)
        flow_id_two = uuid.UUID(flow_id_two)

    res_one = list(flows_client.list_runs(filter_flow_id=flow_id_one))
    assert len(res_one) == meta["by_flow_id"][str(flow_id_one)]["num"]
    for run in res_one:
        assert run["flow_id"] == str(flow_id_one)

    res_two = list(flows_client.list_runs(filter_flow_id=flow_id_two))
    assert len(res_two) == meta["by_flow_id"][str(flow_id_two)]["num"]
    for run in res_two:
        assert run["flow_id"] == str(flow_id_two)

    res_combined = list(
        flows_client.list_runs(filter_flow_id=[flow_id_one, flow_id_two])
    )
    assert len(res_combined) == (
        meta["by_flow_id"][str(flow_id_one)]["num"]
        + meta["by_flow_id"][str(flow_id_two)]["num"]
    )
    for run in res_combined:
        assert run["flow_id"] in {str(flow_id_one), str(flow_id_two)}
