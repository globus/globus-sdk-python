import urllib.parse

import pytest

from globus_sdk import GlobusSDKUsageError, RemovedInV4Warning
from globus_sdk._testing import get_last_request, load_response


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

    if filter_role:
        with pytest.warns(
            RemovedInV4Warning,
            match=r"The `filter_role` parameter is deprecated.*",
        ):
            res = flows_client.list_flows(**add_kwargs)
    else:
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


@pytest.mark.parametrize(
    "orderby_style, orderby_value",
    [
        # single str -> single param
        ("str", "created_at ASC"),
        # sequence of strs (tuple, list) -> multi param
        ("seq", ["created_at ASC", "updated_at DESC"]),
        ("seq", ("created_at ASC", "updated_at DESC")),
        # more complex cases to handle within the test: generators and sets
        ("generator", ("created_at ASC", "updated_at DESC")),
        ("set", ("created_at ASC", "updated_at DESC")),
    ],
)
def test_list_flows_orderby_multi(flows_client, orderby_style, orderby_value):
    meta = load_response(flows_client.list_flows).metadata

    if orderby_style == "str":
        orderby = orderby_value
        expected_orderby_value = [orderby_value]
    elif orderby_style == "seq":
        orderby = orderby_value
        expected_orderby_value = list(orderby_value)
    elif orderby_style == "generator":
        orderby = (x for x in orderby_value)
        expected_orderby_value = list(orderby_value)
    elif orderby_style == "set":
        orderby = set(orderby_value)
        expected_orderby_value = set(orderby_value)
    else:
        raise NotImplementedError

    res = flows_client.list_flows(orderby=orderby)
    assert res.http_status == 200
    # check result correctness
    assert meta["first_flow_id"] == res["flows"][0]["id"]

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)

    # for the set case, handle arbitrary ordering by converting the value seen
    # back to a set
    if isinstance(expected_orderby_value, set):
        assert set(parsed_qs["orderby"]) == expected_orderby_value
    else:
        assert parsed_qs["orderby"] == expected_orderby_value


@pytest.mark.parametrize(
    "filter_role, filter_roles",
    [
        # empty string values
        ("", ""),
        ("", []),
        ("", [""]),
        # single string values
        ("bar", "baz"),
        # list values
        ("bar", ["baz"]),
        ("bar", ["baz", "qux"]),
        # comma-separated string
        ("bar", "baz,qux"),
        # empty list
        ("bar", []),
        # list containing empty string
        ("bar", [""]),
        # list containing multiple empty strings
        ("bar", ["", ""]),
        # list containing mixed values
        ("bar", ["baz", "", "qux"]),
    ],
)
def test_list_flows_mutually_exclusive_roles(flows_client, filter_role, filter_roles):
    with pytest.raises(GlobusSDKUsageError), pytest.warns(RemovedInV4Warning):
        flows_client.list_flows(filter_role=filter_role, filter_roles=filter_roles)


@pytest.mark.parametrize(
    "filter_roles, expected_filter_roles",
    [
        # empty list/tuple, list/tuple with empty string, and None do not send the param
        ((), None),
        ([], None),
        ([""], None),
        (("",), None),
        (None, None),
        # single role as string
        ("foo", ["foo"]),
        # single role as list/tuple
        (["foo"], ["foo"]),
        (("foo",), ["foo"]),
        # multiple roles as comma-separated string
        ("foo,bar", ["foo,bar"]),
        # multiple roles as list/tuple
        (["foo", "bar"], ["foo,bar"]),
        (("foo", "bar"), ["foo,bar"]),
    ],
)
def test_list_flows_with_filter_roles_parameter(
    flows_client, filter_roles, expected_filter_roles
):
    load_response(flows_client.list_flows).metadata

    res = flows_client.list_flows(filter_roles=filter_roles)
    assert res.http_status == 200

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)

    # Only check filter_roles in parsed_qs if we expect a non-empty value
    if expected_filter_roles:
        assert parsed_qs["filter_roles"] == expected_filter_roles
    else:
        assert "filter_roles" not in parsed_qs
