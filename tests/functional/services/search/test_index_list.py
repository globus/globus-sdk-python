import dataclasses
import urllib.parse

import pytest

from globus_sdk._missing import MISSING
from globus_sdk.testing import get_last_request, load_response


def test_search_index_list(client):
    meta = load_response(client.index_list).metadata
    index_ids = meta["index_ids"]

    res = client.index_list()
    assert res.http_status == 200

    index_list = res["index_list"]
    assert isinstance(index_list, list)
    assert len(index_list) == len(index_ids)
    assert [i["id"] for i in index_list] == index_ids


def test_search_index_list_is_iterable(client):
    meta = load_response(client.index_list).metadata
    index_ids = meta["index_ids"]

    res = client.index_list()
    assert res.http_status == 200

    index_list = list(res)
    assert len(index_list) == len(index_ids)
    assert [i["id"] for i in index_list] == index_ids


_OMIT = object()


@dataclasses.dataclass
class FilterRoleParam:
    name: str
    value: object
    expect_parsed_param: object = None

    @property
    def missing(self) -> bool:
        return self.value in (_OMIT, MISSING)

    @property
    def call_kwargs(self) -> dict[str, object]:
        return {} if self.value is _OMIT else {"filter_roles": self.value}

    def __str__(self) -> str:
        return self.name


@pytest.mark.parametrize(
    "filter_param",
    [
        FilterRoleParam("omitted", _OMIT),
        FilterRoleParam("missing", MISSING),
        FilterRoleParam("ownerstr", "owner", ["owner"]),
        FilterRoleParam("adminstr", "admin", ["admin"]),
        FilterRoleParam("writerstr", "writer", ["writer"]),
        FilterRoleParam("tuple", ("owner", "admin"), ["owner,admin"]),
        FilterRoleParam("list", ["admin", "writer"], ["admin,writer"]),
        FilterRoleParam("duplicates", ("admin", "admin"), ["admin,admin"]),
        # this isn't a real role, but it should be passed through as though it were
        # -- this value can be a typing time error but never a runtime error
        FilterRoleParam("unknown_str", "ambassador", ["ambassador"]),
    ],
    ids=str,
)
def test_search_index_list_encodes_filter_roles_as_expected(client, filter_param):
    load_response(client.index_list).metadata
    res = client.index_list(**filter_param.call_kwargs)
    assert res.http_status == 200

    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    if filter_param.missing:
        assert "filter_roles" not in parsed_qs
    else:
        assert parsed_qs["filter_roles"] == filter_param.expect_parsed_param
