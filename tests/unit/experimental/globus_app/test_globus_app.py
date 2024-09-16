from __future__ import annotations

import os
import time
from unittest import mock

import pytest

from globus_sdk import (
    AccessTokenAuthorizer,
    AuthLoginClient,
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
from globus_sdk.experimental.login_flow_manager import (
    CommandLineLoginFlowManager,
    LocalServerLoginFlowManager,
    LoginFlowManager,
)
from globus_sdk.experimental.tokenstorage import (
    JSONTokenStorage,
    MemoryTokenStorage,
    SQLiteTokenStorage,
    TokenData,
)
from globus_sdk.gare import GlobusAuthorizationParameters
from globus_sdk.scopes import AuthScopes, Scope
from globus_sdk.services.auth import OAuthTokenResponse


def _mock_token_data_by_rs():
    return {
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
    mock_client = mock.Mock(
        spec=NativeAppAuthClient,
        client_id="mock-client_id",
        base_url="https://auth.globus.org",
        environment="production",
    )
    user_app = UserApp("test-app", login_client=mock_client)

    assert user_app.app_name == "test-app"
    assert user_app._login_client == mock_client
    assert user_app.client_id == "mock-client_id"


def test_user_app_no_client_or_id():
    msg = (
        "Could not set up a globus login client. One of client_id or login_client is "
        "required."
    )
    with pytest.raises(GlobusSDKUsageError, match=msg):
        UserApp("test-app")


def test_user_app_both_client_and_id():
    msg = "Mutually exclusive parameters: client_id and login_client."
    with pytest.raises(GlobusSDKUsageError, match=msg):
        UserApp("test-app", login_client=mock.Mock(), client_id="client_id")


def test_user_app_login_client_environment_mismatch():
    mock_client = mock.Mock(environment="sandbox")

    with pytest.raises(GlobusSDKUsageError) as exc:
        config = GlobusAppConfig(environment="preview")
        UserApp("test-app", login_client=mock_client, config=config)

    expected = "[Environment Mismatch] The login_client's environment (sandbox) does not match the GlobusApp's configured environment (preview)."  # noqa
    assert str(exc.value) == expected


def test_user_app_default_token_storage():
    client_id = "mock_client_id"
    user_app = UserApp("test-app", client_id=client_id)

    token_storage = user_app._authorizer_factory.token_storage.token_storage
    assert isinstance(token_storage, JSONTokenStorage)

    if os.name == "nt":
        # on the windows-latest run this was
        # C:\Users\runneradmin\AppData\Roaming\globus\app\mock_client_id\test-app\tokens.json
        expected = "\\globus\\app\\mock_client_id\\test-app\\tokens.json"
        assert token_storage.filepath.endswith(expected)
    else:
        expected = "~/.globus/app/mock_client_id/test-app/tokens.json"
        assert token_storage.filepath == os.path.expanduser(expected)


class CustomMemoryTokenStorage(MemoryTokenStorage):
    pass


@pytest.mark.parametrize(
    "token_storage_value, token_storage_class",
    (
        # Named token storage types
        ("json", JSONTokenStorage),
        ("sqlite", SQLiteTokenStorage),
        ("memory", MemoryTokenStorage),
        # Custom token storage class (instantiated or class)
        (CustomMemoryTokenStorage(), CustomMemoryTokenStorage),
        (CustomMemoryTokenStorage, CustomMemoryTokenStorage),
    ),
)
def test_user_app_token_storage_configuration(token_storage_value, token_storage_class):
    client_id = "mock_client_id"
    config = GlobusAppConfig(token_storage=token_storage_value)

    user_app = UserApp("test-app", client_id=client_id, config=config)
    assert isinstance(user_app._token_storage, token_storage_class)


def test_user_app_creates_consent_client():
    client_id = "mock_client_id"
    user_app = UserApp("test-app", client_id=client_id)

    assert user_app.token_storage._consent_client is not None


class MockLoginFlowManager(LoginFlowManager):
    def __init__(self, login_client: AuthLoginClient | None = None):
        login_client = login_client or mock.Mock(spec=NativeAppAuthClient)
        super().__init__(login_client)

    @classmethod
    def for_globus_app(
        cls, app_name: str, login_client: AuthLoginClient, config: GlobusAppConfig
    ) -> MockLoginFlowManager:
        return cls(login_client)

    def run_login_flow(self, auth_parameters: GlobusAuthorizationParameters):
        return mock.Mock()


@pytest.mark.parametrize(
    "value,login_flow_manager_class",
    (
        (None, CommandLineLoginFlowManager),
        ("command-line", CommandLineLoginFlowManager),
        ("local-server", LocalServerLoginFlowManager),
        (MockLoginFlowManager(), MockLoginFlowManager),
        (MockLoginFlowManager, MockLoginFlowManager),
    ),
)
def test_user_app_login_flow_manager_configuration(value, login_flow_manager_class):
    client_id = "mock_client_id"
    config = GlobusAppConfig(login_flow_manager=value)
    user_app = UserApp("test-app", client_id=client_id, config=config)

    assert isinstance(user_app._login_flow_manager, login_flow_manager_class)


def test_user_app_templated():
    client_id = "mock_client_id"
    client_secret = "mock_client_secret"
    config = GlobusAppConfig(login_redirect_uri="https://example.com")
    user_app = UserApp(
        "test-app", client_id=client_id, client_secret=client_secret, config=config
    )

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

    msg = "A ClientApp requires a client_secret to initialize its own login client"
    with pytest.raises(GlobusSDKUsageError, match=msg):
        ClientApp("test-app", client_id=client_id)


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


@pytest.mark.parametrize(
    "scope_collection",
    ("email", AuthScopes.email, Scope("email"), [Scope("email")]),
)
def test_add_scope_requirements_accepts_different_scope_types(scope_collection):
    client_id = "mock_client_id"
    user_app = UserApp("test-app", client_id=client_id)

    assert _sorted_auth_scope_str(user_app) == "openid"

    # Add a scope scope string
    user_app.add_scope_requirements({"auth.globus.org": scope_collection})
    assert _sorted_auth_scope_str(user_app) == "email openid"


@pytest.mark.parametrize(
    "scope_collection",
    ("email", AuthScopes.email, Scope("email"), [Scope("email")]),
)
def test_constructor_scope_requirements_accepts_different_scope_types(scope_collection):
    client_id = "mock_client_id"
    user_app = UserApp(
        "test-app",
        client_id=client_id,
        scope_requirements={"auth.globus.org": scope_collection},
    )

    assert _sorted_auth_scope_str(user_app) == "email openid"


def test_scope_requirements_returns_copies_scopes():
    user_app = UserApp("test-app", client_id="mock_client_id")
    foo_scope = Scope("foo:all").add_dependency(Scope("bar:all"))
    user_app.add_scope_requirements({"foo": [foo_scope]})

    real_requirements = user_app._scope_requirements
    real_openid = real_requirements["auth.globus.org"][0]
    real_foo = real_requirements["foo"][0]

    copied_requirements = user_app.scope_requirements
    copied_openid = copied_requirements["auth.globus.org"][0]
    copied_foo = copied_requirements["foo"][0]

    assert real_requirements is not copied_requirements

    # Copied requirements mirror the originals but are distinct objects.
    assert real_openid is not copied_openid
    assert real_foo is not copied_foo
    assert str(real_openid) == str(copied_openid)
    assert str(real_foo) == str(copied_foo)


def _sorted_auth_scope_str(user_app: UserApp) -> str:
    scope_list = user_app.scope_requirements["auth.globus.org"]
    return " ".join(sorted(str(scope) for scope in scope_list))


def test_user_app_get_authorizer():
    client_id = "mock_client_id"
    memory_storage = MemoryTokenStorage()
    memory_storage.store_token_data_by_resource_server(_mock_token_data_by_rs())
    config = GlobusAppConfig(token_storage=memory_storage)
    user_app = UserApp("test-app", client_id=client_id, config=config)

    authorizer = user_app.get_authorizer("auth.globus.org")
    assert isinstance(authorizer, AccessTokenAuthorizer)
    assert authorizer.access_token == "mock_access_token"


def test_user_app_get_authorizer_clears_cache_when_adding_scope_requirements():
    client_id = "mock_client_id"
    memory_storage = MemoryTokenStorage()
    memory_storage.store_token_data_by_resource_server(_mock_token_data_by_rs())
    config = GlobusAppConfig(token_storage=memory_storage)
    user_app = UserApp("test-app", client_id=client_id, config=config)

    initial_authorizer = user_app.get_authorizer("auth.globus.org")
    assert isinstance(initial_authorizer, AccessTokenAuthorizer)
    assert initial_authorizer.access_token == "mock_access_token"

    # We should've cached the authorizer from the first call
    assert user_app.get_authorizer("auth.globus.org") is initial_authorizer

    user_app.add_scope_requirements({"auth.globus.org": [Scope("openid")]})

    # The cache should've been cleared
    updated_authorizer = user_app.get_authorizer("auth.globus.org")
    assert initial_authorizer is not updated_authorizer
    assert isinstance(updated_authorizer, AccessTokenAuthorizer)
    assert updated_authorizer.access_token == "mock_access_token"

    assert user_app.get_authorizer("auth.globus.org") is updated_authorizer


def test_user_app_get_authorizer_refresh():
    client_id = "mock_client_id"
    memory_storage = MemoryTokenStorage()
    memory_storage.store_token_data_by_resource_server(_mock_token_data_by_rs())
    config = GlobusAppConfig(token_storage=memory_storage, request_refresh_tokens=True)
    user_app = UserApp("test-app", client_id=client_id, config=config)

    authorizer = user_app.get_authorizer("auth.globus.org")
    assert isinstance(authorizer, RefreshTokenAuthorizer)
    assert authorizer.refresh_token == "mock_refresh_token"


class CustomExitException(Exception):
    pass


class RaisingLoginFlowManagerCounter(LoginFlowManager):
    """
    A login flow manager which increments a public counter and raises an exception on
    each login attempt.
    """

    def __init__(self):
        super().__init__(mock.Mock(spec=NativeAppAuthClient))
        self.counter = 0

    def run_login_flow(
        self, auth_parameters: GlobusAuthorizationParameters
    ) -> OAuthTokenResponse:
        self.counter += 1
        raise CustomExitException("mock login attempt")


def test_user_app_expired_authorizer_triggers_login():
    # Set up token data with an expired access token and no refresh token
    client_id = "mock_client_id"
    memory_storage = MemoryTokenStorage()
    token_data = _mock_token_data_by_rs()
    token_data["auth.globus.org"].expires_at_seconds = int(time.time() - 3600)
    token_data["auth.globus.org"].refresh_token = None
    memory_storage.store_token_data_by_resource_server(token_data)

    login_flow_manager = RaisingLoginFlowManagerCounter()
    config = GlobusAppConfig(
        token_storage=memory_storage, login_flow_manager=login_flow_manager
    )
    user_app = UserApp("test-app", client_id=client_id, config=config)

    with pytest.raises(CustomExitException):
        user_app.get_authorizer("auth.globus.org")

    assert login_flow_manager.counter == 1


def test_client_app_get_authorizer():
    client_id = "mock_client_id"
    client_secret = "mock_client_secret"
    memory_storage = MemoryTokenStorage()
    memory_storage.store_token_data_by_resource_server(_mock_token_data_by_rs())
    config = GlobusAppConfig(token_storage=memory_storage)
    client_app = ClientApp(
        "test-app", client_id=client_id, client_secret=client_secret, config=config
    )

    authorizer = client_app.get_authorizer("auth.globus.org")
    assert isinstance(authorizer, ClientCredentialsAuthorizer)
    assert authorizer.confidential_client.client_id == "mock_client_id"


@mock.patch.object(OAuthTokenResponse, "decode_id_token", _mock_decode)
def test_user_app_login_logout(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", _mock_input)
    load_response(NativeAppAuthClient.oauth2_exchange_code_for_tokens, case="openid")
    load_response(NativeAppAuthClient.oauth2_revoke_token)

    client_id = "mock_client_id"
    memory_storage = MemoryTokenStorage()
    config = GlobusAppConfig(token_storage=memory_storage)
    user_app = UserApp("test-app", client_id=client_id, config=config)

    assert memory_storage.get_token_data("auth.globus.org") is None
    assert user_app.login_required() is True

    user_app.login()
    assert memory_storage.get_token_data("auth.globus.org").access_token is not None
    assert user_app.login_required() is False

    user_app.logout()
    assert memory_storage.get_token_data("auth.globus.org") is None
    assert user_app.login_required() is True


@mock.patch.object(OAuthTokenResponse, "decode_id_token", _mock_decode)
def test_client_app_login_logout():
    load_response(
        ConfidentialAppAuthClient.oauth2_client_credentials_tokens, case="openid"
    )
    load_response(ConfidentialAppAuthClient.oauth2_revoke_token)

    client_id = "mock_client_id"
    client_secret = "mock_client_secret"
    memory_storage = MemoryTokenStorage()
    config = GlobusAppConfig(token_storage=memory_storage)
    client_app = ClientApp(
        "test-app", client_id=client_id, client_secret=client_secret, config=config
    )

    assert memory_storage.get_token_data("auth.globus.org") is None

    client_app.login()
    assert memory_storage.get_token_data("auth.globus.org").access_token is not None

    client_app.logout()
    assert memory_storage.get_token_data("auth.globus.org") is None


@mock.patch.object(OAuthTokenResponse, "decode_id_token", _mock_decode)
@pytest.mark.parametrize(
    "login_kwargs,expected_login",
    (
        # No params - no additional login
        ({}, False),
        # "force" or "auth_params" - additional login
        ({"force": True}, True),
        (
            {"auth_params": GlobusAuthorizationParameters(session_required_mfa=True)},
            True,
        ),
    ),
)
def test_app_login_flows_can_be_forced(login_kwargs, expected_login, monkeypatch):
    monkeypatch.setattr("builtins.input", _mock_input)
    load_response(NativeAppAuthClient.oauth2_exchange_code_for_tokens, case="openid")

    config = GlobusAppConfig(
        token_storage="memory",
        login_flow_manager=CountingCommandLineLoginFlowManager,
    )
    user_app = UserApp("test-app", client_id="mock_client_id", config=config)

    user_app.login()
    assert user_app.login_required() is False
    assert user_app._login_flow_manager.counter == 1

    user_app.login(**login_kwargs)
    expected_count = 2 if expected_login else 1
    assert user_app._login_flow_manager.counter == expected_count


class CountingCommandLineLoginFlowManager(CommandLineLoginFlowManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0

    def run_login_flow(
        self,
        auth_parameters: GlobusAuthorizationParameters,
    ) -> OAuthTokenResponse:
        self.counter += 1
        return super().run_login_flow(auth_parameters)
