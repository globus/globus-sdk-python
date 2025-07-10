from globus_sdk.testing import get_last_request, load_response


def test_oauth2_token_introspect(auth_client):
    meta = load_response(auth_client.oauth2_token_introspect).metadata
    response = auth_client.oauth2_token_introspect("some_very_cool_token")
    assert response["username"] == meta["username"]
    assert response["sub"] == meta["id"]

    last_req = get_last_request()
    assert len(last_req.params) == 0


def test_oauth2_token_introspect_allows_added_query_params(auth_client):
    meta = load_response(auth_client.oauth2_token_introspect).metadata
    response = auth_client.oauth2_token_introspect(
        "some_very_cool_token", query_params={"foo": "bar"}
    )
    assert response["username"] == meta["username"]
    assert response["sub"] == meta["id"]

    last_req = get_last_request()
    assert last_req.params["foo"] == "bar"
