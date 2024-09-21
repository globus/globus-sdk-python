import pytest

from globus_sdk.tokenstorage import (
    JSONTokenStorage,
    MemoryTokenStorage,
    SQLiteTokenStorage,
)


@pytest.fixture(params=["json", "sqlite", "memory"])
def storage(request, tmp_path):
    if request.param == "json":
        file = tmp_path / "mydata.json"
        yield JSONTokenStorage(file)
    elif request.param == "sqlite":
        file = tmp_path / "mydata.db"
        store = SQLiteTokenStorage(file)
        yield store
        store.close()
    else:
        yield MemoryTokenStorage()


def test_store_authorization_code_response(
    storage, authorization_code_response, id_token_sub
):
    storage.store_token_response(authorization_code_response)

    tok_by_rs = authorization_code_response.by_resource_server

    stored_data = storage.get_token_data_by_resource_server()

    for resource_server in ["resource_server_1", "resource_server_2"]:
        for fieldname in (
            "resource_server",
            "scope",
            "access_token",
            "refresh_token",
            "expires_at_seconds",
            "token_type",
        ):
            assert tok_by_rs[resource_server][fieldname] == getattr(
                stored_data[resource_server], fieldname
            )
        assert "identity_id" not in tok_by_rs[resource_server]
        assert stored_data[resource_server].identity_id == id_token_sub


def test_store_dependent_token_response(storage, dependent_token_response):
    """
    If a TokenStorage is asked to store dependent token data, it should work and
    produce identity_id values of None (because there is no id_token to inspect)
    """
    storage.store_token_response(dependent_token_response)

    dep_tok_by_rs = dependent_token_response.by_resource_server

    stored_data = storage.get_token_data_by_resource_server()

    for resource_server in ["resource_server_1", "resource_server_2"]:
        for fieldname in (
            "resource_server",
            "scope",
            "access_token",
            "refresh_token",
            "expires_at_seconds",
            "token_type",
        ):
            assert dep_tok_by_rs[resource_server][fieldname] == getattr(
                stored_data[resource_server], fieldname
            )
        assert stored_data[resource_server].identity_id is None
        assert "identity_id" not in dep_tok_by_rs[resource_server]


def test_store_refresh_token_response(storage, refresh_token_response):
    """
    If a TokenStorage is asked to store refresh token data, it should work and
    produce identity_id values of None (because there is no id_token to inspect)
    """
    storage.store_token_response(refresh_token_response)

    refresh_tok_by_rs = refresh_token_response.by_resource_server

    stored_data = storage.get_token_data_by_resource_server()

    for fieldname in (
        "resource_server",
        "scope",
        "access_token",
        "refresh_token",
        "expires_at_seconds",
        "token_type",
    ):
        assert refresh_tok_by_rs["resource_server_1"][fieldname] == getattr(
            stored_data["resource_server_1"], fieldname
        )
    assert stored_data["resource_server_1"].identity_id is None
    assert "identity_id" not in refresh_tok_by_rs["resource_server_1"]
