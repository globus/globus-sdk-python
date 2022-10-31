import urllib.parse

import pytest

from globus_sdk._testing import get_last_request, load_response


def test_get_group(groups_client):
    meta = load_response(groups_client.get_group).metadata

    res = groups_client.get_group(group_id=meta["group_id"])
    assert res.http_status == 200
    assert "Claptrap" in res["name"]


@pytest.mark.parametrize(
    "include_param",
    ["policies", "policies,memberships", ["memberships", "policies", "child_ids"]],
)
def test_get_group_include(groups_client, include_param):
    meta = load_response(groups_client.get_group).metadata
    expect_param = (
        ",".join(include_param) if not isinstance(include_param, str) else include_param
    )

    res = groups_client.get_group(group_id=meta["group_id"], include=include_param)
    assert res.http_status == 200
    assert "Claptrap" in res["name"]

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert len(parsed_qs["include"]) == 1
    assert parsed_qs["include"][0] == expect_param
