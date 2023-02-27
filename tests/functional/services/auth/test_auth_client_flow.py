import urllib.parse

import pytest

import globus_sdk
from globus_sdk._testing import load_response
from globus_sdk.scopes import TransferScopes
from globus_sdk.services.auth.flow_managers.native_app import make_native_app_challenge

CLIENT_ID = "d0f1d9b0-bd81-4108-be74-ea981664453a"


@pytest.fixture
def client(no_retry_transport):
    class CustomAuthClient(globus_sdk.AuthClient):
        transport_class = no_retry_transport

    return CustomAuthClient(client_id=CLIENT_ID)


def test_oauth2_get_authorize_url_native_defaults(client):
    # default parameters for starting auth flow
    # should warn because scopes were not specified
    with pytest.warns(globus_sdk.RemovedInV4Warning):
        flow_manager = globus_sdk.services.auth.GlobusNativeAppFlowManager(client)
    client.current_oauth2_flow_manager = flow_manager

    # get url and validate results
    url_res = client.oauth2_get_authorize_url()
    parsed_url = urllib.parse.urlparse(url_res)
    assert f"https://{parsed_url.netloc}/" == client.base_url
    assert parsed_url.path == "/v2/oauth2/authorize"
    parsed_params = urllib.parse.parse_qs(parsed_url.query)
    assert parsed_params == {
        "client_id": [client.client_id],
        "redirect_uri": [client.base_url + "v2/web/auth-code"],
        "scope": [f"openid profile email {TransferScopes.all}"],
        "state": ["_default"],
        "response_type": ["code"],
        "code_challenge": [flow_manager.challenge],
        "code_challenge_method": ["S256"],
        "access_type": ["online"],
    }


def test_oauth2_get_authorize_url_native_custom_params(client):
    # starting flow with custom parameters, should not warn because a scope is specified
    flow_manager = globus_sdk.services.auth.GlobusNativeAppFlowManager(
        client,
        requested_scopes="scopes",
        redirect_uri="uri",
        state="state",
        verifier=("a" * 43),
        refresh_tokens=True,
    )
    client.current_oauth2_flow_manager = flow_manager

    # get url_and validate results
    url_res = client.oauth2_get_authorize_url()
    verifier, remade_challenge = make_native_app_challenge("a" * 43)
    parsed_url = urllib.parse.urlparse(url_res)
    assert f"https://{parsed_url.netloc}/" == client.base_url
    assert parsed_url.path == "/v2/oauth2/authorize"
    parsed_params = urllib.parse.parse_qs(parsed_url.query)
    assert parsed_params == {
        "client_id": [client.client_id],
        "redirect_uri": ["uri"],
        "scope": ["scopes"],
        "state": ["state"],
        "response_type": ["code"],
        "code_challenge": [urllib.parse.quote_plus(remade_challenge)],
        "code_challenge_method": ["S256"],
        "access_type": ["offline"],
    }


def test_oauth2_get_authorize_url_confidential_defaults(client):
    # default parameters for starting auth flow
    # warns because no requested_scopes was passed
    with pytest.warns(globus_sdk.RemovedInV4Warning):
        flow_manager = globus_sdk.services.auth.GlobusAuthorizationCodeFlowManager(
            client, "uri"
        )
    client.current_oauth2_flow_manager = flow_manager

    # get url_and validate results
    url_res = client.oauth2_get_authorize_url()
    parsed_url = urllib.parse.urlparse(url_res)
    assert f"https://{parsed_url.netloc}/" == client.base_url
    assert parsed_url.path == "/v2/oauth2/authorize"
    parsed_params = urllib.parse.parse_qs(parsed_url.query)
    assert parsed_params == {
        "client_id": [client.client_id],
        "redirect_uri": ["uri"],
        "scope": [f"openid profile email {TransferScopes.all}"],
        "state": ["_default"],
        "response_type": ["code"],
        "access_type": ["online"],
    }


def test_oauth2_get_authorize_url_confidential_custom_params(client):
    # starting flow with specified parameters
    flow_manager = globus_sdk.services.auth.GlobusAuthorizationCodeFlowManager(
        client,
        requested_scopes="scopes",
        redirect_uri="uri",
        state="state",
        refresh_tokens=True,
    )
    client.current_oauth2_flow_manager = flow_manager

    # get url_and validate results
    url_res = client.oauth2_get_authorize_url()
    parsed_url = urllib.parse.urlparse(url_res)
    assert f"https://{parsed_url.netloc}/" == client.base_url
    assert parsed_url.path == "/v2/oauth2/authorize"
    parsed_params = urllib.parse.parse_qs(parsed_url.query)
    assert parsed_params == {
        "client_id": [client.client_id],
        "redirect_uri": ["uri"],
        "scope": ["scopes"],
        "state": ["state"],
        "response_type": ["code"],
        "access_type": ["offline"],
    }


def test_oauth2_exchange_code_for_tokens_native(client):
    """
    Starts a NativeAppFlowManager, Confirms invalid code raises 401
    Further testing cannot be done without user login credentials
    """
    load_response(client.oauth2_exchange_code_for_tokens, case="invalid_grant")

    flow_manager = globus_sdk.services.auth.GlobusNativeAppFlowManager(
        client, requested_scopes=TransferScopes.all
    )
    client.current_oauth2_flow_manager = flow_manager

    with pytest.raises(globus_sdk.AuthAPIError) as excinfo:
        client.oauth2_exchange_code_for_tokens("invalid_code")
    assert excinfo.value.http_status == 401
    assert excinfo.value.code == "Error"


def test_oauth2_exchange_code_for_tokens_confidential(client):
    """
    Starts an AuthorizationCodeFlowManager, Confirms bad code raises 401
    Further testing cannot be done without user login credentials
    """
    load_response(client.oauth2_exchange_code_for_tokens, case="invalid_grant")

    flow_manager = globus_sdk.services.auth.GlobusAuthorizationCodeFlowManager(
        client, "uri", requested_scopes=TransferScopes.all
    )
    client.current_oauth2_flow_manager = flow_manager

    with pytest.raises(globus_sdk.AuthAPIError) as excinfo:
        client.oauth2_exchange_code_for_tokens("invalid_code")
    assert excinfo.value.http_status == 401
    assert excinfo.value.code == "Error"
