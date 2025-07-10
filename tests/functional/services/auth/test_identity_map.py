import pytest
import responses

import globus_sdk
from globus_sdk.testing import get_last_request, load_response

IDENTITIES_MULTIPLE_RESPONSE = {
    "identities": [
        {
            "email": None,
            "id": "46bd0f56-e24f-11e5-a510-131bef46955c",
            "identity_provider": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
            "name": None,
            "organization": None,
            "status": "unused",
            "username": "globus@globus.org",
        },
        {
            "email": "sirosen@globus.org",
            "id": "ae341a98-d274-11e5-b888-dbae3a8ba545",
            "identity_provider": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
            "name": "Stephen Rosen",
            "organization": "Globus Team",
            "status": "used",
            "username": "sirosen@globus.org",
        },
    ]
}


def test_identity_map(service_client):
    meta = load_response(service_client.get_identities, case="sirosen").metadata
    idmap = globus_sdk.IdentityMap(service_client, [meta["username"]])
    assert idmap[meta["username"]]["organization"] == meta["org"]

    # lookup by ID also works
    assert idmap[meta["id"]]["organization"] == meta["org"]

    # the last (only) API call was the one by username
    last_req = get_last_request()
    assert "ids" not in last_req.params
    assert last_req.params == {"usernames": meta["username"], "provision": "false"}


def test_identity_map_initialization_no_values(service_client):
    idmap = globus_sdk.IdentityMap(service_client)
    assert idmap.unresolved_ids == set()
    assert idmap.unresolved_usernames == set()


def test_identity_map_initialization_mixed_and_duplicate_values(service_client):
    # splits things up and deduplicates values into sets
    idmap = globus_sdk.IdentityMap(
        service_client,
        [
            "sirosen@globus.org",
            "ae341a98-d274-11e5-b888-dbae3a8ba545",
            "globus@globus.org",
            "sirosen@globus.org",
            "globus@globus.org",
            "ae341a98-d274-11e5-b888-dbae3a8ba545",
            "sirosen@globus.org",
            "ae341a98-d274-11e5-b888-dbae3a8ba545",
        ],
    )
    assert idmap.unresolved_ids == {"ae341a98-d274-11e5-b888-dbae3a8ba545"}
    assert idmap.unresolved_usernames == {"sirosen@globus.org", "globus@globus.org"}


def test_identity_map_initialization_batch_size(service_client):
    idmap = globus_sdk.IdentityMap(service_client, id_batch_size=10)
    assert idmap.unresolved_ids == set()
    assert idmap.unresolved_usernames == set()
    assert idmap.id_batch_size == 10


def test_identity_map_add(service_client):
    idmap = globus_sdk.IdentityMap(service_client)
    assert idmap.add("sirosen@globus.org") is True
    assert idmap.add("sirosen@globus.org") is False
    assert idmap.add("46bd0f56-e24f-11e5-a510-131bef46955c") is True
    assert idmap.add("46bd0f56-e24f-11e5-a510-131bef46955c") is False


def test_identity_map_add_after_lookup(service_client):
    meta = load_response(service_client.get_identities, case="sirosen").metadata
    idmap = globus_sdk.IdentityMap(service_client)
    x = idmap[meta["username"]]["id"]
    # this is the key: adding it will indicate that we've already seen this ID, perhaps
    # "unintuitively", and that's part of the value of `add()` returning a boolean value
    assert idmap.add(x) is False
    assert idmap[x] == idmap[meta["username"]]


def test_identity_map_multiple(service_client):
    meta = load_response(service_client.get_identities, case="multiple").metadata
    idmap = globus_sdk.IdentityMap(
        service_client, ["sirosen@globus.org", "globus@globus.org"]
    )
    assert idmap["sirosen@globus.org"]["organization"] == "Globus Team"
    assert idmap["globus@globus.org"]["organization"] is None

    last_req = get_last_request()
    # order doesn't matter, but it should be just these two
    # if IdentityMap doesn't deduplicate correctly, it could send
    # `sirosen@globus.org,globus@globus.org,sirosen@globus.org` on the first lookup
    assert last_req.params["usernames"].split(",") in [
        meta["usernames"],
        meta["usernames"][::-1],
    ]
    assert last_req.params["provision"] == "false"


def test_identity_map_keyerror(service_client):
    load_response(service_client.get_identities, case="sirosen")
    idmap = globus_sdk.IdentityMap(service_client)
    # a name which doesn't come back, indicating that it was not found, will KeyError
    with pytest.raises(KeyError):
        idmap["sirosen2@globus.org"]

    last_req = get_last_request()
    assert last_req.params == {"usernames": "sirosen2@globus.org", "provision": "false"}


def test_identity_map_get_with_default(service_client):
    load_response(service_client.get_identities, case="sirosen")
    magic = object()  # sentinel value
    idmap = globus_sdk.IdentityMap(service_client)
    # a name which doesn't come back, if looked up with `get()` should return the
    # default
    assert idmap.get("sirosen2@globus.org", magic) is magic


def test_identity_map_del(service_client):
    meta = load_response(service_client.get_identities).metadata
    idmap = globus_sdk.IdentityMap(service_client)
    identity_id = idmap[meta["username"]]["id"]
    del idmap[identity_id]
    assert idmap.get(meta["username"])["id"] == identity_id
    # we've only made one request so far
    assert len(responses.calls) == 1
    # but a lookup by ID after a del is going to trigger another request because we've
    # invalidated the cached ID data and are asking the IDMap to look it up again
    assert idmap.get(identity_id)["username"] == meta["username"]
    assert len(responses.calls) == 2


@pytest.mark.parametrize(
    "lookup1,lookup2",
    [
        ("username", "username"),
        ("username", "id"),
        ("id", "username"),
    ],
)
@pytest.mark.parametrize("initial_add", [True, False])
def test_identity_map_shared_cache_match(service_client, initial_add, lookup1, lookup2):
    meta = load_response(service_client.get_identities, case="sirosen").metadata
    lookup1, lookup2 = meta[lookup1], meta[lookup2]
    cache = {}
    idmap1 = globus_sdk.IdentityMap(service_client, cache=cache)
    idmap2 = globus_sdk.IdentityMap(service_client, cache=cache)
    if initial_add:
        idmap1.add(lookup1)
        idmap2.add(lookup2)
    # no requests yet...
    assert len(responses.calls) == 0
    # do the first lookup, it should make one request
    assert idmap1[lookup1]["organization"] == meta["org"]
    assert len(responses.calls) == 1
    # lookup more values and make sure that "everything matches"
    assert idmap2[lookup2]["organization"] == meta["org"]
    assert idmap1[lookup1]["id"] == idmap2[lookup2]["id"]
    assert idmap1[lookup2]["id"] == idmap2[lookup1]["id"]
    # we've only made one request, because the shared cache captured this info on the
    # very first call
    assert len(responses.calls) == 1


@pytest.mark.parametrize(
    "lookup_style",
    ["usernames", "ids"],
)
def test_identity_map_shared_cache_mismatch(service_client, lookup_style):
    meta = load_response(service_client.get_identities, case="multiple").metadata
    lookup1, lookup2 = meta[lookup_style]
    cache = {}
    idmap1 = globus_sdk.IdentityMap(service_client, [lookup1, lookup2], cache=cache)
    idmap2 = globus_sdk.IdentityMap(service_client, cache=cache)
    # no requests yet...
    assert len(responses.calls) == 0
    # do the first lookup, it should make one request
    assert lookup1 in (idmap1[lookup1]["id"], idmap1[lookup1]["username"])
    assert len(responses.calls) == 1
    # lookup more values and make sure that "everything matches"
    assert lookup2 in (idmap2[lookup2]["id"], idmap2[lookup2]["username"])
    assert idmap1[lookup1]["id"] == idmap2[lookup1]["id"]
    assert idmap1[lookup2]["id"] == idmap2[lookup2]["id"]
    # we've only made one request, because the shared cache captured this info on the
    # very first call
    assert len(responses.calls) == 1


def test_identity_map_prepopulated_cache(service_client):
    meta = load_response(service_client.get_identities).metadata

    # populate the cache, even with nulls it should stop any lookups from happening
    cache = {meta["id"]: None, meta["username"]: None}
    idmap = globus_sdk.IdentityMap(service_client, cache=cache)
    # no requests yet...
    assert len(responses.calls) == 0
    # do the lookups
    assert idmap[meta["id"]] is None
    assert idmap[meta["username"]] is None
    # still no calls made
    assert len(responses.calls) == 0


def test_identity_map_batch_limit(service_client):
    meta1 = load_response(service_client.get_identities).metadata
    meta2 = load_response(service_client.get_identities, case="sirosen").metadata

    # setup the ID map with a size limit of 1
    idmap = globus_sdk.IdentityMap(service_client, id_batch_size=1)
    idmap.add(meta2["id"])
    idmap.add(meta1["id"])

    # no requests yet...
    assert len(responses.calls) == 0

    # do the first lookup, using the second ID to be added
    # only one call should be made
    assert idmap[meta1["id"]]["username"] == meta1["username"]
    assert len(responses.calls) == 1
    # 1 ID left unresolved
    assert len(idmap.unresolved_ids) == 1
    # the last (only) API call was by ID with one ID
    last_req = get_last_request()
    assert "usernames" not in last_req.params
    assert last_req.params == {"ids": meta1["id"]}

    # second lookup works as well
    assert idmap[meta2["id"]]["username"] == meta2["username"]
    assert len(responses.calls) == 2
    # no IDs left unresolved
    assert len(idmap.unresolved_ids) == 0
    # the last API call was by ID with one ID
    last_req = get_last_request()
    assert "usernames" not in last_req.params
    assert last_req.params == {"ids": meta2["id"]}
