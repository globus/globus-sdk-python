"""
Test that globus_sdk.testing can accept a non-default requests mock
"""

import pytest
import requests
import responses

from globus_sdk import GlobusHTTPResponse, GroupsClient
from globus_sdk.testing import get_last_request, load_response


@pytest.fixture
def custom_requests_mock():
    responses.stop()

    with responses.RequestsMock() as m:
        yield m


def test_get_last_request_on_empty_custom_mock_returns_none(custom_requests_mock):
    assert get_last_request(requests_mock=custom_requests_mock) is None


def test_get_last_request_on_custom_mock_populated_via_manual_load(
    custom_requests_mock,
):
    custom_requests_mock.add("GET", "https://example.org/", json={"foo": "bar"})
    r = requests.get("https://example.org/")
    assert r.json() == {"foo": "bar"}

    req = get_last_request(requests_mock=custom_requests_mock)
    assert req is not None
    assert req.body is None  # "example" assertion about a request


def test_register_client_method_and_call_on_custom_mock(custom_requests_mock):
    gc = GroupsClient()
    loaded = load_response(gc.get_group, requests_mock=custom_requests_mock)

    group_id = loaded.metadata["group_id"]
    data = gc.get_group(group_id)

    assert isinstance(data, GlobusHTTPResponse)
