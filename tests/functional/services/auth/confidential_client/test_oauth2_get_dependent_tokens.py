import urllib.parse

import pytest

from globus_sdk.testing import get_last_request, load_response


def test_oauth2_get_dependent_tokens(auth_client):
    meta = load_response(
        auth_client.oauth2_get_dependent_tokens, case="groups"
    ).metadata

    response = auth_client.oauth2_get_dependent_tokens("dummy_token")
    full_response_by_rs = response.by_resource_server

    # data matches fully in the by_resource_server layout
    expected_data = meta["rs_data"]
    assert set(expected_data) == set(full_response_by_rs)
    for rs_name, values in expected_data.items():
        assert full_response_by_rs[rs_name]["access_token"] == values["access_token"]
        assert full_response_by_rs[rs_name]["scope"] == values["scope"]


def test_oauth2_get_dependent_tokens_with_refresh_token(auth_client):
    meta = load_response(
        auth_client.oauth2_get_dependent_tokens, case="groups_with_refresh_token"
    ).metadata

    response = auth_client.oauth2_get_dependent_tokens(
        "dummy_token", refresh_tokens=True
    )
    full_response_by_rs = response.by_resource_server

    # data matches fully in the by_resource_server layout
    expected_data = meta["rs_data"]
    assert set(expected_data) == set(full_response_by_rs)
    for rs_name, values in expected_data.items():
        assert full_response_by_rs[rs_name]["access_token"] == values["access_token"]
        assert full_response_by_rs[rs_name]["refresh_token"] == values["refresh_token"]
        assert full_response_by_rs[rs_name]["scope"] == values["scope"]

    # parse sent request and ensure that refresh_tokens translated correctly
    # to `access_type=offline`
    last_req = get_last_request()
    assert last_req.body
    body = last_req.body
    assert body != ""
    parsed_body = urllib.parse.parse_qs(body)
    assert parsed_body["access_type"] == ["offline"]


@pytest.mark.parametrize(
    "scope_arg, expect_value",
    [(None, None), ("scope1", "scope1"), (("scope1", "scope2"), "scope1 scope2")],
)
def test_oauth2_get_dependent_tokens_scope_string_param(
    auth_client, scope_arg, expect_value
):
    load_response(auth_client.oauth2_get_dependent_tokens, case="groups")

    add_args = {}
    if scope_arg is not None:
        add_args["scope"] = scope_arg
    auth_client.oauth2_get_dependent_tokens("dummy_token", **add_args)

    last_req = get_last_request()
    assert last_req.body
    body = last_req.body
    assert body != ""
    parsed_body = urllib.parse.parse_qs(body)
    if expect_value is None:
        assert "scope" not in parsed_body
    else:
        assert parsed_body["scope"] == [expect_value]
