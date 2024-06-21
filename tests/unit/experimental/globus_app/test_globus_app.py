import os
import time
from unittest import mock

import pytest

from globus_sdk import (
    AccessTokenAuthorizer,
    ClientCredentialsAuthorizer,
    ConfidentialAppAuthClient,
    NativeAppAuthClient,
    RefreshTokenAuthorizer,
)
from globus_sdk._testing import load_response
from globus_sdk.exc import GlobusSDKUsageError
from globus_sdk.experimental.globus_app import (
    AccessTokenAuthorizerFactory,
    ClientApp,
    ClientCredentialsAuthorizerFactory,
    GlobusAppConfig,
    RefreshTokenAuthorizerFactory,
    UserApp,
)
from globus_sdk.experimental.login_flow_manager import CommandLineLoginFlowManager
from globus_sdk.experimental.tokenstorage import (
    JSONTokenStorage,
    MemoryTokenStorage,
    TokenData,
)
from globus_sdk.scopes import Scope
from globus_sdk.services.auth import OAuthTokenResponse

_mock_token_data_by_rs = {
    "auth.globus.org": TokenData(
        resource_server="auth.globus.org",
        identity_id="mock_identity_id",
        scope="openid",
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        expires_at_seconds=int(time.time() + 300),
        token_type="Bearer",
    )
}


def _mock_input(s):
    print(s)
    return "mock_input"


def _mock_decode(*args, **kwargs):
    return {"sub": "user_id"}


def test_user_app_native():
    client_id = "mock_client_id"
    user_app = UserApp("test-app", client_id=client_id)

    assert user_app.app_name == "test-app"
    assert isinstance(user_app._login_client, NativeAppAuthClient)
    assert user_app._login_client.app_name == "test-app"
    assert isinstance(user_app._authorizer_factory, AccessTokenAuthorizerFactory)
    assert isinstance(user_app._login_flow_manager, CommandLineLoginFlowManager)


def test_user_app_login_client():
    mock_client = mock.Mock()
    user_app = UserApp("test-app", login_client=mock_client)

    assert user_app.app_name == "test-app"
    assert user_app._login_client == mock_client


def test_user_app_no_client_or_id():
    with pytest.raises(GlobusSDKUsageError) as exc:
        UserApp("test-app")
    assert str(exc.value) == "One of either client_id or login_client is required."


def test_user_app_both_client_and_id():
    client_id = "mock_client_id"
    mock_client = mock.Mock()

    with pytest.raises(GlobusSDKUsageError) as exc:
        UserApp("test-app", login_client=mock_client, client_id=client_id)
    assert (
        str(exc.value)
        == "login_client is mutually exclusive with client_id and client_secret."
    )


def test_user_app_default_token_storage():
    client_id = "mock_client_id"
    user_app = UserApp("test-app", client_id=client_id)

    token_storage = user_app._authorizer_factory.token_storage._token_storage
    assert isinstance(token_storage, JSONTokenStorage)
    if os.name == "nt":
        # on the windows-latest run this was
        # C:\Users\runneradmin\AppData\Roaming\globus\app\test-app\tokens.json
        assert "\\globus\\app\\test-app\\tokens.json" in token_storage.filename
    else:
        assert token_storage.filename == os.path.expanduser(
            "~/.globus/app/test-app/tokens.json"
        )


def test_user_app_templated():
    client_id = "mock_client_id"
    client_secret = "mock_client_secret"
    user_app = UserApp("test-app", client_id=client_id, client_secret=client_secret)

    assert user_app.app_name == "test-app"
    assert isinstance(user_app._login_client, ConfidentialAppAuthClient)
    assert user_app._login_client.app_name == "test-app"
    assert isinstance(user_app._authorizer_factory, AccessTokenAuthorizerFactory)
    assert isinstance(user_app._login_flow_manager, CommandLineLoginFlowManager)


def test_user_app_refresh():
    client_id = "mock_client_id"
    config = GlobusAppConfig(request_refresh_tokens=True)
    user_app = UserApp("test-app", client_id=client_id, config=config)

    assert user_app.app_name == "test-app"
    assert isinstance(user_app._login_client, NativeAppAuthClient)
    assert user_app._login_client.app_name == "test-app"
    assert isinstance(user_app._authorizer_factory, RefreshTokenAuthorizerFactory)


def test_client_app():
    client_id = "mock_client_id"
    client_secret = "mock_client_secret"
    client_app = ClientApp("test-app", client_id=client_id, client_secret=client_secret)

    assert client_app.app_name == "test-app"
    assert isinstance(client_app._login_client, ConfidentialAppAuthClient)
    assert client_app._login_client.app_name == "test-app"
    assert isinstance(
        client_app._authorizer_factory, ClientCredentialsAuthorizerFactory
    )


def test_client_app_no_secret():
    client_id = "mock_client_id"

    with pytest.raises(GlobusSDKUsageError) as exc:
        ClientApp("test-app", client_id=client_id)
    assert (
        str(exc.value)
        == "Either login_client or both client_id and client_secret are required"
    )


def test_add_scope_requirements_and_auth_params_with_required_scopes():
    client_id = "mock_client_id"
    user_app = UserApp("test-app", client_id=client_id)

    # default without adding requirements is just auth's openid scope
    params = user_app._auth_params_with_required_scopes()
    assert params.required_scopes == ["openid"]

    # re-adding openid alongside other auth scopes, openid shouldn't be duplicated
    user_app.add_scope_requirements(
        {"auth.globus.org": [Scope("openid"), Scope("email"), Scope("profile")]}
    )
    params = user_app._auth_params_with_required_scopes()
    assert sorted(params.required_scopes) == ["email", "openid", "profile"]

    # adding a requirement with a dependency
    user_app.add_scope_requirements(
        {"foo": [Scope("foo:all").add_dependency(Scope("bar:all"))]}
    )
    params = user_app._auth_params_with_required_scopes()
    assert sorted(params.required_scopes) == [
        "email",
        "foo:all[bar:all]",
        "openid",
        "profile",
    ]

    # re-adding a requirement with a new dependency, dependencies should be combined
    user_app.add_scope_requirements(
        {"foo": [Scope("foo:all").add_dependency(Scope("baz:all"))]}
    )
    params = user_app._auth_params_with_required_scopes()
    # order of dependencies is not guaranteed
    assert sorted(params.required_scopes) in (
        ["email", "foo:all[bar:all baz:all]", "openid", "profile"],
        ["email", "foo:all[baz:all bar:all]", "openid", "profile"],
    )


def test_user_app_get_authorizer():
    client_id = "mock_client_id"
    memory_storage = MemoryTokenStorage()
    memory_storage.store_token_data_by_resource_server(_mock_token_data_by_rs)
    config = GlobusAppConfig(token_storage=memory_storage)
    user_app = UserApp("test-app", client_id=client_id, config=config)

    authorizer = user_app.get_authorizer("auth.globus.org")
    assert isinstance(authorizer, AccessTokenAuthorizer)
    assert authorizer.access_token == "mock_access_token"


def test_user_app_get_authorizer_refresh():
    client_id = "mock_client_id"
    memory_storage = MemoryTokenStorage()
    memory_storage.store_token_data_by_resource_server(_mock_token_data_by_rs)
    config = GlobusAppConfig(token_storage=memory_storage, request_refresh_tokens=True)
    user_app = UserApp("test-app", client_id=client_id, config=config)

    authorizer = user_app.get_authorizer("auth.globus.org")
    assert isinstance(authorizer, RefreshTokenAuthorizer)
    assert authorizer.refresh_token == "mock_refresh_token"


def test_client_app_get_authorizer():
    client_id = "mock_client_id"
    client_secret = "mock_client_secret"
    memory_storage = MemoryTokenStorage()
    memory_storage.store_token_data_by_resource_server(_mock_token_data_by_rs)
    config = GlobusAppConfig(token_storage=memory_storage)
    client_app = ClientApp(
        "test-app", client_id=client_id, client_secret=client_secret, config=config
    )

    authorizer = client_app.get_authorizer("auth.globus.org")
    assert isinstance(authorizer, ClientCredentialsAuthorizer)
    assert authorizer.confidential_client.client_id == "mock_client_id"


@mock.patch.object(OAuthTokenResponse, "decode_id_token", _mock_decode)
def test_user_app_run_login_flow(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", _mock_input)
    load_response(NativeAppAuthClient.oauth2_exchange_code_for_tokens, case="openid")

    client_id = "mock_client_id"
    memory_storage = MemoryTokenStorage()
    config = GlobusAppConfig(token_storage=memory_storage)
    user_app = UserApp("test-app", client_id=client_id, config=config)

    user_app.run_login_flow()
    assert (
        user_app._token_storage.get_token_data("auth.globus.org").access_token
        == "auth_access_token"
    )


@mock.patch.object(OAuthTokenResponse, "decode_id_token", _mock_decode)
def test_client_app_run_login_flow():
    load_response(
        ConfidentialAppAuthClient.oauth2_client_credentials_tokens, case="openid"
    )

    client_id = "mock_client_id"
    client_secret = "mock_client_secret"
    memory_storage = MemoryTokenStorage()
    config = GlobusAppConfig(token_storage=memory_storage)
    client_app = ClientApp(
        "test-app", client_id=client_id, client_secret=client_secret, config=config
    )

    client_app.run_login_flow()
    assert (
        client_app._token_storage.get_token_data("auth.globus.org").access_token
        == "auth_access_token"
    )
