from __future__ import annotations

import typing as t
import uuid
from unittest.mock import MagicMock, Mock

import pytest

import globus_sdk
from globus_sdk import (
    GlobusAppConfig,
    IDTokenDecoder,
    NativeAppAuthClient,
    OAuthTokenResponse,
    TransferClient,
    UserApp,
)
from globus_sdk.gare import GlobusAuthorizationParameters
from globus_sdk.login_flows import LoginFlowManager
from globus_sdk.scopes import Scope, TransferScopes
from globus_sdk.testing import RegisteredResponse
from globus_sdk.token_storage import MemoryTokenStorage, TokenStorageData


class GlobusAppConfigurator:

    def __init__(
        self,
        starting_tokens: dict[str, list[Scope]] | None = None,
        login_tokens: dict[str, list[Scope]] | None = None,
    ) -> None:
        self.identity_id = str(uuid.uuid4())

        self.token_storage = MemoryTokenStorage()
        if starting_tokens:
            self.token_storage.store_token_data_by_resource_server(
                {
                    resource_server: self._generate_token_data(resource_server, scopes)
                    for resource_server, scopes in starting_tokens.items()
                }
            )
        self._login_tokens: list[TokenStorageData] = [
            self._generate_token_data(resource_server, scopes)
            for resource_server, scopes in login_tokens.items() or {}.items()
        ]
        self.login_flow_manager = _FakeLoginFlowManager(self._login_tokens)

    def _generate_token_data(
        self, resource_server: str, scopes: list[Scope]
    ) -> TokenStorageData:
        return TokenStorageData(
            identity_id=self.identity_id,
            resource_server=resource_server,
            scope=" ".join(str(s) for s in scopes),
            access_token="generated-access-token",
            refresh_token="generated-refresh-token",
            expires_at_seconds=9999999999,
            token_type="Bearer",
        )

    def config(self, **kwargs: t.Any) -> GlobusAppConfig:
        decoder = MagicMock(spec=IDTokenDecoder)
        decoder.decode.return_value = {"sub": self.identity_id}

        return GlobusAppConfig(
            login_flow_manager=self.login_flow_manager,
            id_token_decoder=decoder,
            token_storage=self.token_storage,
            **kwargs,
        )


class _FakeLoginFlowManager(LoginFlowManager):

    def __init__(self, starting_tokens: list[TokenStorageData]) -> None:
        super().__init__(login_client=MagicMock(spec=NativeAppAuthClient))
        self._by_resource_server = {
            token.resource_server: token.to_dict() for token in starting_tokens
        }
        self.login_count = 0

    def run_login_flow(
        self, auth_parameters: GlobusAuthorizationParameters
    ) -> OAuthTokenResponse:
        self.login_count += 1
        response = Mock()
        response.id_token = "abcdefghjiklmnop"
        response.by_resource_server = self._by_resource_server
        return response


_GET_TASK_SUCCESS_RESPONSE = RegisteredResponse(
    service="transfer",
    path="/v0.10/task/foobar",
    method="GET",
    json={"task_id": "foobar"},
)

_GET_TASK_GARE_RESPONSE = RegisteredResponse(
    service="transfer",
    path="/v0.10/task/foobar",
    method="GET",
    status=403,
    json={
        "code": "AuthorizationRequired",
        "authorization_parameters": {"required_scopes": ["my-cool-new-scope"]},
    },
)


def test_app_can_redrive_gares():
    """
    When enabled:
    If an app-registered client encounters a GARE-compatible 403 http response, it
    should "redrive" it by:
    1. Running a login flow with the gare-included authorization
    2. Re-attempting the original request with the new token(s)
    """
    transfer_rs = TransferClient.resource_server
    configurator = GlobusAppConfigurator(
        # Start with a valid Transfer:all token
        starting_tokens={transfer_rs: [TransferScopes.all]},
        # On login, receive both Transfer:all and the gare-required scope
        login_tokens={transfer_rs: [TransferScopes.all, Scope("my-cool-new-scope")]},
    )
    config = configurator.config(auto_redrive_gares=True)

    app = UserApp(client_id="client_id", config=config)
    transfer = TransferClient(app=app)

    # Set up first a GARE response, then a successful response (on retry)
    _GET_TASK_GARE_RESPONSE.add()
    _GET_TASK_SUCCESS_RESPONSE.add()
    assert transfer.get_task("foobar").http_status == 200
    assert configurator.login_flow_manager.login_count == 1


def test_app_gare_redriving_is_disabled_by_default():
    transfer_rs = TransferClient.resource_server
    configurator = GlobusAppConfigurator(
        # Start with a valid Transfer:all token
        starting_tokens={transfer_rs: [TransferScopes.all]},
        # On login, receive both Transfer:all and the gare-required scope
        login_tokens={transfer_rs: [TransferScopes.all, Scope("my-cool-new-scope")]},
    )
    # Don't override the `auto_redrive_gares` default of False
    config = configurator.config()

    app = UserApp(client_id="client_id", config=config)
    transfer = TransferClient(app=app)

    # Set up first a GARE response, then a successful response (on retry)
    _GET_TASK_GARE_RESPONSE.add()
    _GET_TASK_SUCCESS_RESPONSE.add()
    with pytest.raises(globus_sdk.GlobusAPIError):
        transfer.get_task("foobar")
    assert configurator.login_flow_manager.login_count == 0


def test_app_gare_redrive_only_occurs_once_per_request():
    transfer_rs = TransferClient.resource_server
    configurator = GlobusAppConfigurator(
        # Start with a valid Transfer:all token
        starting_tokens={transfer_rs: [TransferScopes.all]},
        # On login, receive Transfer:all and a random scope (not required by the gare).
        login_tokens={transfer_rs: [TransferScopes.all, Scope("my-stupid-new-scope")]},
    )
    config = configurator.config(auto_redrive_gares=True)

    app = UserApp(client_id="client_id", config=config)
    transfer = TransferClient(app=app)

    # Set up exclusively a GARE response which will retry indefinitely.
    _GET_TASK_GARE_RESPONSE.add()
    with pytest.raises(globus_sdk.GlobusAPIError):
        transfer.get_task("foobar")
    assert configurator.login_flow_manager.login_count == 1
