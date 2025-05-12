import urllib.parse

import pytest

from globus_sdk._testing import RegisteredResponse, get_last_request, load_response
from tests.common import GO_EP1_ID


def _mk_item(*, name, typ, size=0):
    return {
        "DATA_TYPE": "file",
        "group": "tutorial",
        "last_modified": "2018-04-04 18:30:26+00:00",
        "link_group": None,
        "link_last_modified": None,
        "link_size": None,
        "link_target": None,
        "link_user": None,
        "name": name,
        "permissions": "0755" if typ == "dir" else "0644",
        "size": 4096 if typ == "dir" else size,
        "type": typ,
        "user": "snork",
    }


def _mk_ls_data():
    return {
        "DATA": [
            _mk_item(name="foo", typ="dir"),
            _mk_item(name="tempdir1", typ="dir"),
            _mk_item(name=".bashrc", typ="file", size=3771),
            _mk_item(name=".profile", typ="file", size=807),
        ]
    }


@pytest.fixture(autouse=True)
def _setup_ls_response():
    load_response(
        RegisteredResponse(
            service="transfer",
            path=f"/v0.10/operation/endpoint/{GO_EP1_ID}/ls",
            json=_mk_ls_data(),
        ),
    )


def test_operation_ls(client):
    ls_path = f"https://transfer.api.globus.org/v0.10/operation/endpoint/{GO_EP1_ID}/ls"

    # load the tutorial endpoint ls doc
    ls_doc = client.operation_ls(GO_EP1_ID)

    # check that the result is an iterable of file and dir dict objects
    for x in ls_doc:
        assert "DATA_TYPE" in x
        assert x["DATA_TYPE"] in ("file", "dir")

    req = get_last_request()
    assert req.url == ls_path


@pytest.mark.parametrize(
    "kwargs, expected_qs",
    [
        # orderby with a single str
        ({"orderby": "name"}, {"orderby": ["name"]}),
        # orderby with a multiple strs
        (
            {"orderby": ["size DESC", "name", "type"]},
            {"orderby": ["size DESC,name,type"]},
        ),
        # orderby + filter
        (
            {"orderby": "name", "filter": "name:~*.png"},
            {"orderby": ["name"], "filter": ["name:~*.png"]},
        ),
        # local_user
        (
            {"local_user": "my-user"},
            {"local_user": ["my-user"]},
        ),
        # limit+offset
        (
            {"limit": 10, "offset": 5},
            {"limit": ["10"], "offset": ["5"]},
        ),
    ],
)
def test_operation_ls_params(client, kwargs, expected_qs):
    client.operation_ls(GO_EP1_ID, **kwargs)
    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert parsed_qs == expected_qs
