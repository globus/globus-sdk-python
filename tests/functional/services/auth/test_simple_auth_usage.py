import uuid

import pytest

import globus_sdk
from globus_sdk._testing import get_last_request, load_response


class StringWrapper:
    """Simple test object to be a non-string obj wrapping a string"""

    def __init__(self, s):
        self.s = s

    def __str__(self):
        return self.s


@pytest.fixture
def client(no_retry_transport):
    class CustomAuthClient(globus_sdk.AuthClient):
        transport_class = no_retry_transport

    return CustomAuthClient()


def test_get_identities_unauthorized(client):
    data = load_response(client.get_identities, case="unauthorized")

    with pytest.raises(globus_sdk.AuthAPIError) as excinfo:
        client.get_identities(usernames="foobar@example.com")

    err = excinfo.value
    assert err.code == "UNAUTHORIZED"
    assert data.metadata["error_id"] in err.raw_text
    assert err.raw_json == data.json


@pytest.mark.parametrize(
    "usernames",
    [
        "globus@globus.org",
        StringWrapper("globus@globus.org"),
        ["globus@globus.org"],
        ("globus@globus.org",),
    ],
)
def test_get_identities_success(usernames, client):
    data = load_response(client.get_identities)
    res = client.get_identities(usernames=usernames)

    assert [x["id"] for x in res] == [data.metadata["id"]]

    lastreq = get_last_request()
    assert lastreq.params == {
        "usernames": "globus@globus.org",
        "provision": "false",  # provision defaults to false
    }


@pytest.mark.parametrize(
    "inval, outval",
    [
        (True, "true"),
        (False, "false"),
        (1, "true"),
        (0, "true"),
        ("fALSe", "false"),
        ("true", "true"),
    ],
)
def test_get_identities_provision(inval, outval, client):
    load_response(client.get_identities)
    client.get_identities(usernames="globus@globus.org", provision=inval)
    lastreq = get_last_request()
    assert "provision" in lastreq.params
    assert lastreq.params["provision"] == outval


@pytest.mark.parametrize(
    "usernames",
    [
        "globus@globus.org,sirosen@globus.org",
        (StringWrapper("sirosen@globus.org"), StringWrapper("globus@globus.org")),
        ["globus@globus.org", "sirosen@globus.org"],
    ],
)
def test_get_identities_multiple_usernames_success(usernames, client):
    data = load_response(client.get_identities, case="multiple")
    if isinstance(usernames, str):
        expect_param = usernames
    else:
        expect_param = ",".join([str(x) for x in usernames])

    res = client.get_identities(usernames=usernames)

    assert [x["username"] for x in res] == data.metadata["usernames"]
    assert [x["id"] for x in res] == data.metadata["ids"]

    lastreq = get_last_request()
    assert "usernames" in lastreq.params
    assert lastreq.params["usernames"] == expect_param


@pytest.mark.parametrize(
    "ids",
    [
        # two uuids, already comma delimited
        ",".join(
            [
                "46bd0f56-e24f-11e5-a510-131bef46955c",
                "ae341a98-d274-11e5-b888-dbae3a8ba545",
            ]
        ),
        # a list of two UUID objects
        [
            uuid.UUID("46bd0f56-e24f-11e5-a510-131bef46955c"),
            uuid.UUID("ae341a98-d274-11e5-b888-dbae3a8ba545"),
        ],
    ],
)
def test_get_identities_multiple_ids_success(ids, client):
    data = load_response(client.get_identities, case="multiple")
    expect_param = ",".join(data.metadata["ids"])

    res = client.get_identities(ids=ids)

    assert [x["id"] for x in res] == data.metadata["ids"]
    assert [x["username"] for x in res] == data.metadata["usernames"]

    lastreq = get_last_request()
    assert "ids" in lastreq.params
    assert lastreq.params["ids"] == expect_param
