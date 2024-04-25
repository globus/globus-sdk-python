from unittest.mock import Mock, patch

from globus_sdk import ConfidentialAppAuthClient, NativeAppAuthClient
from globus_sdk._testing import load_response
from globus_sdk.experimental.auth_requirements_error import (
    GlobusAuthorizationParameters,
)
from globus_sdk.experimental.login_flow_manager import (
    CommandLineLoginFlowManager,
    LocalServerLoginFlowManager,
)


def _mock_input(s):
    print(s)
    return "mock_input"


def test_command_line_login_flower_manager_native(monkeypatch, capsys):
    """
    test CommandLineLoginFlowManager with a NativeAppAuthClient
    """
    login_client = NativeAppAuthClient("mock_client_id")
    load_response(login_client.oauth2_exchange_code_for_tokens)
    monkeypatch.setattr("builtins.input", _mock_input)

    custom_login_prompt = "Login:"
    custom_code_prompt = "Code:"
    login_flow_manager = CommandLineLoginFlowManager(
        login_client,
        login_prompt=custom_login_prompt,
        code_prompt=custom_code_prompt,
    )
    auth_params = GlobusAuthorizationParameters(
        required_scopes=["urn:globus:auth:scope:transfer.api.globus.org:all"],
        session_required_identities=["user@org.edu"],
    )
    token_res = login_flow_manager.run_login_flow(auth_params)
    assert (
        token_res.by_resource_server["transfer.api.globus.org"]["access_token"]
        == "transfer_access_token"
    )

    captured_output = capsys.readouterr().out
    assert custom_login_prompt in captured_output
    assert custom_code_prompt in captured_output
    assert "https://auth.globus.org/v2/oauth2/authorize" in captured_output
    assert "client_id=mock_client_id" in captured_output
    assert "&session_required_identities=user%40org.edu" in captured_output


def test_command_line_login_flower_manager_confidential(monkeypatch, capsys):
    """
    test CommandLineLoginFlowManager with a ConfidentialAppAuthClient
    """
    login_client = ConfidentialAppAuthClient(
        client_id="mock_client_id", client_secret="mock_client_secret"
    )
    load_response(login_client.oauth2_exchange_code_for_tokens)
    monkeypatch.setattr("builtins.input", _mock_input)

    login_flow_manager = CommandLineLoginFlowManager(login_client)
    auth_params = GlobusAuthorizationParameters(
        required_scopes=["urn:globus:auth:scope:transfer.api.globus.org:all"],
        session_required_single_domain=["org.edu"],
    )
    token_res = login_flow_manager.run_login_flow(auth_params)
    assert (
        token_res.by_resource_server["transfer.api.globus.org"]["access_token"]
        == "transfer_access_token"
    )

    captured_output = capsys.readouterr().out
    assert "Please authenticate with Globus here:" in captured_output
    assert "Enter the resulting Authorization Code here:" in captured_output
    assert "https://auth.globus.org/v2/oauth2/authorize" in captured_output
    assert "client_id=mock_client_id" in captured_output
    assert "&session_required_single_domain=org.edu" in captured_output


class MockRedirectServer:
    def __init__(self, *args, **kwargs):
        self.socket = Mock()
        self.socket.getsockname.return_value = ("", 0)

    def serve_forever(self):
        pass

    def shutdown(self):
        pass

    def wait_for_code(self):
        return "auth_code"


@patch(
    "globus_sdk.experimental.login_flow_manager.local_server_login_flow_manager._open_webbrowser",  # noqa E501
    new=lambda url: None,
)
@patch(
    "globus_sdk.experimental.login_flow_manager.local_server_login_flow_manager.RedirectHTTPServer",  # noqa E501
    new=MockRedirectServer,
)
def test_local_server_login_flower_manager_native():
    """
    test LocalServerLoginManager with a NativeAppAuthClient
    """
    login_client = NativeAppAuthClient("mock_client_id")
    load_response(login_client.oauth2_exchange_code_for_tokens)
    login_flow_manager = LocalServerLoginFlowManager(
        login_client,
    )
    auth_params = GlobusAuthorizationParameters(
        required_scopes=["urn:globus:auth:scope:transfer.api.globus.org:all"],
    )
    token_res = login_flow_manager.run_login_flow(auth_params)
    assert (
        token_res.by_resource_server["transfer.api.globus.org"]["access_token"]
        == "transfer_access_token"
    )


@patch(
    "globus_sdk.experimental.login_flow_manager.local_server_login_flow_manager._open_webbrowser",  # noqa E501
    new=lambda url: None,
)
@patch(
    "globus_sdk.experimental.login_flow_manager.local_server_login_flow_manager.RedirectHTTPServer",  # noqa E501
    new=MockRedirectServer,
)
def test_local_server_login_flower_manager_confidential():
    """
    test LocalServerLoginManager with a ConfidentialAppAuthClient
    """
    login_client = ConfidentialAppAuthClient(
        client_id="mock_client_id", client_secret="mock_client_secret"
    )
    load_response(login_client.oauth2_exchange_code_for_tokens)
    login_flow_manager = LocalServerLoginFlowManager(
        login_client,
    )
    auth_params = GlobusAuthorizationParameters(
        required_scopes=["urn:globus:auth:scope:transfer.api.globus.org:all"],
    )
    token_res = login_flow_manager.run_login_flow(auth_params)
    assert (
        token_res.by_resource_server["transfer.api.globus.org"]["access_token"]
        == "transfer_access_token"
    )
