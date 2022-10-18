import datetime
import sys
import typing as t
import urllib.parse
import uuid

import pytest
from responses import matchers

from globus_sdk._testing import (
    get_last_request,
    load_response,
    load_response_set,
    register_response_set,
)

OWNER_ID = "e061df5a-b7b9-4578-a73b-6d4a4edfd66e"


def generate_hello_world_example_flow(n: int) -> t.Dict[str, t.Any]:
    flow_id = str(uuid.UUID(int=n))
    if sys.version_info < (3, 7):
        # old branch which pyupgrade will remove when we drop py3.6
        base_time = datetime.datetime(
            2021, 10, 18, 19, 19, 35, 967289, tzinfo=datetime.timezone.utc
        )
    else:
        base_time = datetime.datetime.fromisoformat("2021-10-18T19:19:35.967289+00:00")
    updated_at = created_at = base_time + datetime.timedelta(days=n)
    flow_user_scope = (
        f"https://auth.globus.org/scopes/{flow_id}/"
        f"flow_{flow_id.replace('-', '_')}_user"
    )

    return {
        "action_url": f"https://flows.automate.globus.org/flows/{flow_id}",
        "administered_by": [],
        "api_version": "1.0",
        "created_at": created_at.isoformat() + "+00:00",
        "created_by": f"urn:globus:auth:identity:{OWNER_ID}",
        "definition": {
            "StartAt": "HelloWorld",
            "States": {
                "HelloWorld": {
                    "ActionScope": (
                        "https://auth.globus.org/scopes/actions.globus.org/hello_world"
                    ),
                    "ActionUrl": "https://actions.globus.org/hello_world",
                    "End": True,
                    "Parameters": {"echo_string": "Hello, World."},
                    "ResultPath": "$.Result",
                    "Type": "Action",
                }
            },
        },
        "description": "A simple Flow...",
        "flow_administrators": [],
        "flow_owner": f"urn:globus:auth:identity:{OWNER_ID}",
        "flow_starters": [],
        "flow_url": f"https://flows.automate.globus.org/flows/{flow_id}",
        "flow_viewers": [],
        "globus_auth_scope": flow_user_scope,
        "globus_auth_username": f"{flow_id}@clients.auth.globus.org",
        "id": str(flow_id),
        "input_schema": {
            "additionalProperties": False,
            "properties": {
                "echo_string": {"description": "The string to echo", "type": "string"},
                "sleep_time": {"type": "integer"},
            },
            "required": ["echo_string", "sleep_time"],
            "type": "object",
        },
        "keywords": [],
        "log_supported": True,
        "principal_urn": f"urn:globus:auth:identity:{flow_id}",
        "runnable_by": [],
        "subtitle": "",
        "synchronous": False,
        "title": f"Hello, World (Example {n})",
        "types": ["Action"],
        "updated_at": updated_at.isoformat() + "+00:00",
        "user_role": "flow_viewer",
        "visible_to": [],
    }


@pytest.fixture(autouse=True, scope="session")
def setup_paginated_responses() -> None:
    register_response_set(
        "list_flows_paginated",
        {
            "page0": dict(
                service="flows",
                path="/flows",
                json={
                    "flows": [generate_hello_world_example_flow(i) for i in range(20)],
                    "limit": 20,
                    "has_next_page": True,
                    "marker": "fake_marker_0",
                },
            ),
            "page1": dict(
                service="flows",
                path="/flows",
                json={
                    "flows": [
                        generate_hello_world_example_flow(i) for i in range(20, 40)
                    ],
                    "limit": 20,
                    "has_next_page": True,
                    "marker": "fake_marker_1",
                },
                match=[matchers.query_param_matcher({"marker": "fake_marker_0"})],
            ),
            "page2": dict(
                service="flows",
                path="/flows",
                json={
                    "flows": [
                        generate_hello_world_example_flow(i) for i in range(40, 60)
                    ],
                    "limit": 20,
                    "has_next_page": False,
                    "marker": None,
                },
                match=[matchers.query_param_matcher({"marker": "fake_marker_1"})],
            ),
        },
        metadata={
            "owner_id": OWNER_ID,
            "num_pages": 3,
            "expect_markers": ["fake_marker_0", "fake_marker_1", None],
            "total_items": 60,
        },
    )


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
    meta = load_response_set("list_flows_paginated").metadata
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
