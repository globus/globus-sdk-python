import uuid

import pytest

import globus_sdk
from globus_sdk import GlobusApp, GlobusAppConfig, UserApp
from globus_sdk._testing import load_response
from globus_sdk.token_storage import MemoryTokenStorage


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

    with pytest.raises(globus_sdk.GlobusSDKUsageError) as exc:
        globus_sdk.AuthClient(app=app, environment="preview")

    expected = "[Environment Mismatch] AuthClient's environment (preview) does not match the GlobusApp's configured environment (sandbox)."  # noqa: E501
    assert str(exc.value) == expected


def test_transfer_client_default_scopes(app):
    globus_sdk.TransferClient(app=app)

    assert [str(s) for s in app.scope_requirements["transfer.api.globus.org"]] == [
        "urn:globus:auth:scope:transfer.api.globus.org:all"
    ]


def test_transfer_client_add_app_data_access_scope(app):
    client = globus_sdk.TransferClient(app=app)

    collection_id = str(uuid.UUID(int=0))
    client.add_app_data_access_scope(collection_id)
    str_list = [str(s) for s in app.scope_requirements["transfer.api.globus.org"]]
    expected = f"urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/{collection_id}/data_access]"  # noqa: E501
    assert expected in str_list


def test_timers_client_add_app_data_access_scope(app):
    client = globus_sdk.TimersClient(app=app)

    collection_id = str(uuid.UUID(int=0))
    client.add_app_transfer_data_access_scope(collection_id)
    str_list = [
        str(s) for s in app.scope_requirements[globus_sdk.TimersClient.resource_server]
    ]
    expected = f"{globus_sdk.TimersClient.scopes.timer}[urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/{collection_id}/data_access]]"  # noqa: E501
    assert expected in str_list


def test_specific_flow_client_add_app_data_access_scope(app):
    flow_id = str(uuid.UUID(int=1))
    client = globus_sdk.SpecificFlowClient(flow_id, app=app)

    collection_id = str(uuid.UUID(int=0))
    client.add_app_transfer_data_access_scope(collection_id)
    str_list = [str(s) for s in app.scope_requirements[client.resource_server]]
    expected = f"{client.scopes.user}[*urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/{collection_id}/data_access]]"  # noqa: E501
    assert expected in str_list


def test_transfer_client_add_app_data_access_scope_chaining(app):
    collection_id_1 = str(uuid.UUID(int=1))
    collection_id_2 = str(uuid.UUID(int=2))
    (
        globus_sdk.TransferClient(app=app)
        .add_app_data_access_scope(collection_id_1)
        .add_app_data_access_scope(collection_id_2)
    )

    str_list = [str(s) for s in app.scope_requirements["transfer.api.globus.org"]]
    expected_1 = f"urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/{collection_id_1}/data_access]"  # noqa: E501
    expected_2 = f"urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/{collection_id_2}/data_access]"  # noqa: E501
    assert expected_1 in str_list
    assert expected_2 in str_list


def test_transfer_client_add_app_data_access_scope_in_iterable(app):
    collection_id_1 = str(uuid.UUID(int=1))
    collection_id_2 = str(uuid.UUID(int=2))
    globus_sdk.TransferClient(app=app).add_app_data_access_scope(
        (collection_id_1, collection_id_2)
    )

    expected_1 = f"https://auth.globus.org/scopes/{collection_id_1}/data_access"
    expected_2 = f"https://auth.globus.org/scopes/{collection_id_2}/data_access"

    transfer_dependencies = []
    for scope in app.scope_requirements["transfer.api.globus.org"]:
        if scope.scope_string != str(globus_sdk.TransferClient.scopes.all):
            continue
        for dep in scope.dependencies:
            transfer_dependencies.append((dep.scope_string, dep.optional))

    assert (expected_1, True) in transfer_dependencies
    assert (expected_2, True) in transfer_dependencies


def test_timers_client_add_app_data_access_scope_in_iterable(app):
    collection_id_1 = str(uuid.UUID(int=1))
    collection_id_2 = str(uuid.UUID(int=2))
    globus_sdk.TimersClient(app=app).add_app_transfer_data_access_scope(
        (collection_id_1, collection_id_2)
    )

    expected_1 = f"https://auth.globus.org/scopes/{collection_id_1}/data_access"
    expected_2 = f"https://auth.globus.org/scopes/{collection_id_2}/data_access"

    transfer_dependencies = []
    for scope in app.scope_requirements[globus_sdk.TimersClient.resource_server]:
        if scope.scope_string != str(globus_sdk.TimersClient.scopes.timer):
            continue
        for dep in scope.dependencies:
            if dep.scope_string != str(globus_sdk.TransferClient.scopes.all):
                continue
            for subdep in dep.dependencies:
                transfer_dependencies.append((subdep.scope_string, subdep.optional))

    assert (expected_1, True) in transfer_dependencies
    assert (expected_2, True) in transfer_dependencies


def test_transfer_client_add_app_data_access_scope_catches_bad_uuid(app):
    with pytest.raises(ValueError, match="'collection_ids' must be a valid UUID"):
        globus_sdk.TransferClient(app=app).add_app_data_access_scope("foo")


def test_transfer_client_add_app_data_access_scope_catches_bad_uuid_in_iterable(app):
    collection_id_1 = str(uuid.UUID(int=1))
    with pytest.raises(ValueError, match=r"'collection_ids\[1\]' must be a valid UUID"):
        globus_sdk.TransferClient(app=app).add_app_data_access_scope(
            [collection_id_1, "foo"]
        )


def test_timers_client_add_app_data_access_scope_catches_bad_uuid(app):
    with pytest.raises(ValueError, match="'collection_ids' must be a valid UUID"):
        globus_sdk.TimersClient(app=app).add_app_transfer_data_access_scope("foo")


def test_timers_client_add_app_data_access_scope_catches_bad_uuid_in_iterable(app):
    collection_id_1 = str(uuid.UUID(int=1))
    with pytest.raises(ValueError, match=r"'collection_ids\[1\]' must be a valid UUID"):
        globus_sdk.TimersClient(app=app).add_app_transfer_data_access_scope(
            [collection_id_1, "foo"]
        )


def test_auth_client_default_scopes(app):
    globus_sdk.AuthClient(app=app)

    str_list = [str(s) for s in app.scope_requirements["auth.globus.org"]]
    assert "openid" in str_list
    assert "profile" in str_list
    assert "email" in str_list


def test_groups_client_default_scopes(app):
    globus_sdk.GroupsClient(app=app)

    assert [str(s) for s in app.scope_requirements["groups.api.globus.org"]] == [
        "urn:globus:auth:scope:groups.api.globus.org:view_my_groups_and_memberships"
    ]


def test_search_client_default_scopes(app):
    globus_sdk.SearchClient(app=app)

    assert [str(s) for s in app.scope_requirements["search.api.globus.org"]] == [
        "urn:globus:auth:scope:search.api.globus.org:search"
    ]


def test_timer_client_default_scopes(app):
    globus_sdk.TimersClient(app=app)

    timer_client_id = "524230d7-ea86-4a52-8312-86065a9e0417"
    str_list = [str(s) for s in app.scope_requirements[timer_client_id]]
    assert str_list == [f"https://auth.globus.org/scopes/{timer_client_id}/timer"]


def test_flows_client_default_scopes(app):
    globus_sdk.FlowsClient(app=app)

    flows_client_id = "eec9b274-0c81-4334-bdc2-54e90e689b9a"
    str_list = [str(s) for s in app.scope_requirements["flows.globus.org"]]
    assert len(str_list) == 1
    assert str_list == [f"https://auth.globus.org/scopes/{flows_client_id}/all"]


def test_specific_flow_client_default_scopes(app):
    globus_sdk.SpecificFlowClient("flow_id", app=app)

    assert [str(s) for s in app.scope_requirements["flow_id"]] == [
        "https://auth.globus.org/scopes/flow_id/flow_flow_id_user"
    ]


def test_gcs_client_default_scopes(app):
    meta = load_response(globus_sdk.GCSClient.get_gcs_info).metadata
    endpoint_client_id = meta["endpoint_client_id"]
    domain_name = meta["domain_name"]

    globus_sdk.GCSClient(domain_name, app=app)

    assert [str(s) for s in app.scope_requirements[endpoint_client_id]] == [
        f"urn:globus:auth:scope:{endpoint_client_id}:manage_collections"
    ]
