import urllib.parse

import pytest

from globus_sdk._testing import get_last_request, load_response


@pytest.mark.parametrize("filter_fulltext", [None, "foo"])
@pytest.mark.parametrize("filter_role", [None, "bar"])
def test_list_flows_simple(flows_client, filter_fulltext, filter_role):
    meta = load_response(flows_client.list_flows).metadata

    add_kwargs = {}
    if filter_fulltext:
        add_kwargs["filter_fulltext"] = filter_fulltext
    if filter_role:
        add_kwargs["filter_role"] = filter_role

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
        for k, v in (("filter_fulltext", filter_fulltext), ("filter_role", filter_role))
        if v is not None
    }
    assert parsed_qs == expect_query_params
