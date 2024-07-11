import pytest

import globus_sdk
from globus_sdk import GlobusSDKUsageError
from globus_sdk._testing import load_response
from globus_sdk.experimental.globus_app import GlobusApp, GlobusAppConfig, UserApp
from globus_sdk.experimental.tokenstorage import MemoryTokenStorage


@pytest.fixture
def app() -> GlobusApp:
    config = GlobusAppConfig(token_storage=MemoryTokenStorage())
    return UserApp("test-app", client_id="client_id", config=config)


def test_client_inherits_environment_from_globus_app():
    config = GlobusAppConfig(token_storage=MemoryTokenStorage(), environment="sandbox")
    app = UserApp("test-app", client_id="client_id", config=config)

    client = globus_sdk.AuthClient(app=app)

    assert client.environment == "sandbox"


def test_client_environment_does_not_match_the_globus_app_environment():
    config = GlobusAppConfig(token_storage=MemoryTokenStorage(), environment="sandbox")
    app = UserApp("test-app", client_id="client_id", config=config)

    with pytest.raises(GlobusSDKUsageError) as exc:
        globus_sdk.AuthClient(app=app, environment="preview")

    expected = "[Environment Mismatch] AuthClient's environment (preview) does not match the GlobusApp's configuredenvironment (sandbox)."  # noqa
    assert str(exc.value) == expected


def test_transfer_client_default_scopes(app):
    globus_sdk.TransferClient(app=app)

    assert [str(s) for s in app.get_scope_requirements("transfer.api.globus.org")] == [
        "urn:globus:auth:scope:transfer.api.globus.org:all"
    ]


def test_transfer_client_add_app_data_access_scope(app):
    client = globus_sdk.TransferClient(app=app)

    client.add_app_data_access_scope("collection_id")
    str_list = [str(s) for s in app.get_scope_requirements("transfer.api.globus.org")]
    expected = "urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/collection_id/data_access]"  # noqa
    assert expected in str_list


def test_transfer_client_add_app_data_access_scope_chaining(app):
    (
        globus_sdk.TransferClient(app=app)
        .add_app_data_access_scope("collection_id_1")
        .add_app_data_access_scope("collection_id_2")
    )

    str_list = [str(s) for s in app.get_scope_requirements("transfer.api.globus.org")]
    expected_1 = "urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/collection_id_1/data_access]"  # noqa
    expected_2 = "urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/collection_id_2/data_access]"  # noqa
    assert expected_1 in str_list
    assert expected_2 in str_list


def test_auth_client_default_scopes(app):
    globus_sdk.AuthClient(app=app)

    str_list = [str(s) for s in app.get_scope_requirements("auth.globus.org")]
    assert "openid" in str_list
    assert "profile" in str_list
    assert "email" in str_list


def test_groups_client_default_scopes(app):
    globus_sdk.GroupsClient(app=app)

    assert [str(s) for s in app.get_scope_requirements("groups.api.globus.org")] == [
        "urn:globus:auth:scope:groups.api.globus.org:view_my_groups_and_memberships"
    ]


def test_search_client_default_scopes(app):
    globus_sdk.SearchClient(app=app)

    assert [str(s) for s in app.get_scope_requirements("search.api.globus.org")] == [
        "urn:globus:auth:scope:search.api.globus.org:search"
    ]


def test_timer_client_default_scopes(app):
    globus_sdk.TimerClient(app=app)

    timer_client_id = "524230d7-ea86-4a52-8312-86065a9e0417"
    str_list = [str(s) for s in app.get_scope_requirements(timer_client_id)]
    assert str_list == [f"https://auth.globus.org/scopes/{timer_client_id}/timer"]


def test_flows_client_default_scopes(app):
    globus_sdk.FlowsClient(app=app)

    flows_client_id = "eec9b274-0c81-4334-bdc2-54e90e689b9a"
    str_list = [str(s) for s in app.get_scope_requirements("flows.globus.org")]
    assert len(str_list) == 2
    assert f"https://auth.globus.org/scopes/{flows_client_id}/view_flows" in str_list
    assert f"https://auth.globus.org/scopes/{flows_client_id}/run_status" in str_list


def test_specific_flow_client_default_scopes(app):
    globus_sdk.SpecificFlowClient("flow_id", app=app)

    assert [str(s) for s in app.get_scope_requirements("flow_id")] == [
        "https://auth.globus.org/scopes/flow_id/flow_flow_id_user"
    ]


def test_gcs_client_default_scopes(app):
    meta = load_response(globus_sdk.GCSClient.get_gcs_info).metadata
    endpoint_client_id = meta["endpoint_client_id"]
    domain_name = meta["domain_name"]

    globus_sdk.GCSClient(domain_name, app=app)

    assert [str(s) for s in app.get_scope_requirements(endpoint_client_id)] == [
        f"urn:globus:auth:scope:{endpoint_client_id}:manage_collections"
    ]
