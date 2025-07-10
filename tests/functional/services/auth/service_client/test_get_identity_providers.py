import pytest

import globus_sdk
from globus_sdk.testing import get_last_request, load_response


def test_get_identity_providers_by_domains(service_client):
    meta = load_response(service_client.get_identity_providers).metadata
    res = service_client.get_identity_providers(domains=meta["domains"])

    assert [x["id"] for x in res] == meta["ids"]

    lastreq = get_last_request()
    assert lastreq.params == {"domains": ",".join(meta["domains"])}


def test_get_identity_providers_by_ids(service_client):
    meta = load_response(service_client.get_identity_providers).metadata
    res = service_client.get_identity_providers(ids=meta["ids"])

    assert [x["id"] for x in res] == meta["ids"]
    assert [x for y in res for x in y["domains"]] == meta["domains"]

    lastreq = get_last_request()
    assert lastreq.params == {"ids": ",".join(meta["ids"])}


def test_get_identity_providers_mutex_args(service_client):
    with pytest.raises(globus_sdk.GlobusSDKUsageError, match="mutually exclusive"):
        service_client.get_identity_providers(ids="foo", domains="bar")


def test_get_identity_providers_allows_query_params_with_no_args(service_client):
    # this test confirms that the request won't be rejected for passing arguments
    # without specifying either 'ids' or 'domains' -- the supposition being that some
    # other parameter is supported but unknown to the SDK
    meta = load_response(service_client.get_identity_providers).metadata
    res = service_client.get_identity_providers(query_params={"foo": "bar,baz,snork"})

    assert [x["id"] for x in res] == meta["ids"]
    assert [x for y in res for x in y["domains"]] == meta["domains"]

    lastreq = get_last_request()
    assert lastreq.params == {"foo": "bar,baz,snork"}
