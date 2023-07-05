import urllib.parse
import uuid

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


@pytest.fixture
def native_client(no_retry_transport):
    class CustomAuthClient(globus_sdk.NativeAppAuthClient):
        transport_class = no_retry_transport

    return CustomAuthClient(client_id=CLIENT_ID)


@pytest.fixture
def confidential_client(no_retry_transport):
    class CustomAuthClient(globus_sdk.ConfidentialAppAuthClient):
        transport_class = no_retry_transport

    return CustomAuthClient(
        client_id=CLIENT_ID, client_secret="SECRET_SECRET_HES_GOT_A_SECRET"
    )


# build a partial matrix over
#
#   domain: str | list[str]
#   identities: uuid | str | list[uuid] | list[str] | list[str | uuid]
#   policies: uuid | str | list[uuid] | list[str] | list[str | uuid]
#
# start by seeding a small set of combinations of params to test, then run some loops to
# fill in the rest
_ALL_SESSION_PARAM_COMBINATIONS = [
    (None, None, None),
    ("foo-id", "bar-id", "baz-id"),
    (["foo-id", "bar-id"], None, ["quux-id", "snork-id"]),
    (None, ["foo-id", "bar-id"], ["quux-id", "snork-id"]),
]
for domain_option in (None, "example.edu", ["example.edu", "example.org"]):
    _ALL_SESSION_PARAM_COMBINATIONS.append((domain_option, None, None))
for identity_option in (
    None,
    uuid.UUID(int=0),
    "foo-id",
    [uuid.UUID(int=0), uuid.UUID(int=1)],
    ["foo-id", "bar-id"],
    ["foo-id", uuid.UUID(int=2)],
):
    _ALL_SESSION_PARAM_COMBINATIONS.append((None, identity_option, None))
for policy_option in (
    None,
    uuid.UUID(int=3),
    "baz-id",
    [uuid.UUID(int=3), uuid.UUID(int=4)],
    ["baz-id", "quux-id"],
    ["baz-id", uuid.UUID(int=5)],
):
    _ALL_SESSION_PARAM_COMBINATIONS.append((None, None, policy_option))


@pytest.mark.parametrize("flow_type", ("native_app", "confidential_app"))
# parametrize over both what is and what *is not* passed as a parameter
@pytest.mark.parametrize(
    "domain_option, identity_option, policy_option", _ALL_SESSION_PARAM_COMBINATIONS
)
def test_oauth2_get_authorize_url_supports_session_params(
    native_client,
    confidential_client,
    flow_type,
    domain_option,
    identity_option,
    policy_option,
):
    if flow_type == "native_app":
        client = native_client
    elif flow_type == "confidential_app":
        client = confidential_client
    else:
        raise NotImplementedError

    # get the url...
    client.oauth2_start_flow(redirect_uri="https://example.com", requested_scopes="foo")
    url_res = client.oauth2_get_authorize_url(
        session_required_single_domain=domain_option,
        session_required_identities=identity_option,
        session_required_policies=policy_option,
    )

    # parse the result..
    parsed_url = urllib.parse.urlparse(url_res)
    parsed_params = urllib.parse.parse_qs(parsed_url.query)

    # prepare some helper data...
    expected_params_keys = {
        "session_required_single_domain" if domain_option else None,
        "session_required_identities" if identity_option else None,
        "session_required_policies" if policy_option else None,
    }
    expected_params_keys.discard(None)
    unexpected_query_params = {
        "session_required_single_domain",
        "session_required_identities",
        "session_required_policies",
    } - expected_params_keys
    parsed_params_keys = set(parsed_params.keys())

    # ...and validate!
    assert expected_params_keys <= parsed_params_keys
    assert (unexpected_query_params - parsed_params_keys) == unexpected_query_params

    if domain_option is not None:
        strized_option = (
            ",".join(str(x) for x in domain_option)
            if isinstance(domain_option, list)
            else str(domain_option)
        )
        assert parsed_params["session_required_single_domain"] == [strized_option]

    if identity_option is not None:
        strized_option = (
            ",".join(str(x) for x in identity_option)
            if isinstance(identity_option, list)
            else str(identity_option)
        )
        assert parsed_params["session_required_identities"] == [strized_option]

    if policy_option is not None:
        strized_option = (
            ",".join(str(x) for x in policy_option)
            if isinstance(policy_option, list)
            else str(policy_option)
        )
        assert parsed_params["session_required_policies"] == [strized_option]


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
