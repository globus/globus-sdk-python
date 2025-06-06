import urllib.parse

import pytest

from globus_sdk._testing import get_last_request, load_response


@pytest.mark.parametrize(
    "client_kwargs, qs",
    [
        ({}, {}),
        ({"query_params": {"foo": "bar"}}, {"foo": "bar"}),
        ({"filter": "foo"}, {"filter": "foo"}),
        ({"limit": 10, "offset": 100}, {"limit": "10", "offset": "100"}),
        ({"limit": 10, "query_params": {"limit": 100}}, {"limit": "100"}),
        ({"filter": "foo:bar:baz"}, {"filter": "foo:bar:baz"}),
        ({"filter": {"foo": "bar", "bar": "baz"}}, {"filter": "foo:bar/bar:baz"}),
        ({"filter": {"foo": ["bar", "baz"]}}, {"filter": "foo:bar,baz"}),
    ],
)
def test_task_list(client, client_kwargs, qs):
    load_response(client.task_list)
    client.task_list(**client_kwargs)

    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    # parsed_qs will have each value as a list (because query-params are a multidict)
    # so transform the test data to match before comparison
    assert parsed_qs == {k: [v] for k, v in qs.items()}


@pytest.mark.parametrize(
    "orderby_value, expected_orderby_param",
    [
        ("foo", "foo"),
        (["foo"], "foo"),
        ("foo,bar", "foo,bar"),
        ("foo ASC,bar", "foo ASC,bar"),
        (["foo ASC", "bar"], "foo ASC,bar"),
        (["foo ASC", "bar DESC"], "foo ASC,bar DESC"),
    ],
)
def test_task_list_orderby_parameter(client, orderby_value, expected_orderby_param):
    load_response(client.task_list)
    client.task_list(orderby=orderby_value)

    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert "orderby" in parsed_qs
    assert len(parsed_qs["orderby"]) == 1
    orderby_param = parsed_qs["orderby"][0]
    assert orderby_param == expected_orderby_param
