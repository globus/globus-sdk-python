import os
import time
from unittest import mock

from globus_sdk import (
    AccessTokenAuthorizer,
    ClientCredentialsAuthorizer,
    ConfidentialAppAuthClient,
    NativeAppAuthClient,
    RefreshTokenAuthorizer,
)
from globus_sdk._testing import load_response
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


def test_user_app_default_token_storage():
    client_id = "mock_client_id"
    user_app = UserApp("test-app", client_id=client_id)

    token_storage = user_app._authorizer_factory.token_storage._token_storage
    assert isinstance(token_storage, JSONTokenStorage)
    if os.name == "nt":
        # on the windows-latest run this was
        # C:\Users\runneradmin\AppData\Roaming\globus\test-app\tokens.json
        assert "\\globus\\test-app\\tokens.json" in token_storage.filename
    else:
        assert token_storage.filename == os.path.expanduser(
            "~/.globus/test-app/tokens.json"
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
    config = GlobusAppConfig(refresh_tokens=True)
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


def test_add_scope_requirements():
    client_id = "mock_client_id"
    user_app = UserApp("test-app", client_id=client_id)
    auth_rs = "auth.globus.org"

    # default without adding requirements is just auth's openid scope
    expected = ["openid"]
    assert [s.serialize() for s in user_app._scope_requirements[auth_rs]] == expected
    assert [
        s.serialize()
        for s in user_app._validating_token_storage.scope_requirements[auth_rs]
    ] == expected

    # re-adding openid alongside other auth scopes, openid shouldn't be duplicated
    user_app.add_scope_requirements(
        {"auth.globus.org": [Scope("openid"), Scope("email"), Scope("profile")]}
    )
    expected = ["email", "openid", "profile"]
    assert (
        sorted([s.serialize() for s in user_app._scope_requirements[auth_rs]])
        == expected
    )
    assert (
        sorted(
            [
                s.serialize()
                for s in user_app._validating_token_storage.scope_requirements[auth_rs]
            ]
        )
        == expected
    )

    # adding a requirement with a dependency
    user_app.add_scope_requirements(
        {"foo": [Scope("foo:all").add_dependency(Scope("bar:all"))]}
    )
    expected = ["foo:all[bar:all]"]
    assert [s.serialize() for s in user_app._scope_requirements["foo"]] == expected
    assert [
        s.serialize()
        for s in user_app._validating_token_storage.scope_requirements["foo"]
    ] == expected

    # re-adding a requirement with a new dependency, dependencies should be combined
    user_app.add_scope_requirements(
        {"foo": [Scope("foo:all").add_dependency(Scope("baz:all"))]}
    )
    expected = [["foo:all[bar:all baz:all]"], ["foo:all[baz:all bar:all]"]]
    assert [s.serialize() for s in user_app._scope_requirements["foo"]] in expected
    assert [
        s.serialize()
        for s in user_app._validating_token_storage.scope_requirements["foo"]
    ] in expected


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
    config = GlobusAppConfig(token_storage=memory_storage, refresh_tokens=True)
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
