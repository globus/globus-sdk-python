import globus_sdk
from globus_sdk.experimental.globus_app import UserApp


def test_transfer_client_default_scopes():
    app = UserApp("test-app", client_id="client_id")
    globus_sdk.TransferClient(app=app)

    assert [str(s) for s in app._scope_requirements["transfer.api.globus.org"]] == [
        "urn:globus:auth:scope:transfer.api.globus.org:all"
    ]


def test_transfer_client_add_app_data_access_scope():
    app = UserApp("test-app", client_id="client_id")
    client = globus_sdk.TransferClient(app=app)

    client.add_app_data_access_scope("collection_id")
    assert [str(s) for s in app._scope_requirements["transfer.api.globus.org"]] == [
        "urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/collection_id/data_access]"  # noqa
    ]


def test_auth_client_default_scopes():
    app = UserApp("test-app", client_id="client_id")
    globus_sdk.AuthClient(app=app)

    str_list = [str(s) for s in app._scope_requirements["auth.globus.org"]]
    assert len(str_list) == 3
    assert "openid" in str_list
    assert "profile" in str_list
    assert "email" in str_list


def test_groups_client_default_scopes():
    app = UserApp("test-app", client_id="client_id")
    globus_sdk.GroupsClient(app=app)

    assert [str(s) for s in app._scope_requirements["groups.api.globus.org"]] == [
        "urn:globus:auth:scope:groups.api.globus.org:view_my_groups_and_memberships"
    ]


def test_search_client_default_scopes():
    app = UserApp("test-app", client_id="client_id")
    globus_sdk.SearchClient(app=app)

    assert [str(s) for s in app._scope_requirements["search.api.globus.org"]] == [
        "urn:globus:auth:scope:search.api.globus.org:search"
    ]


def test_timer_client_default_scopes():
    app = UserApp("test-app", client_id="client_id")
    globus_sdk.TimerClient(app=app)

    assert [
        str(s) for s in app._scope_requirements["524230d7-ea86-4a52-8312-86065a9e0417"]
    ] == ["https://auth.globus.org/scopes/524230d7-ea86-4a52-8312-86065a9e0417/timer"]


def test_flows_client_default_scopes():
    app = UserApp("test-app", client_id="client_id")
    globus_sdk.FlowsClient(app=app)

    str_list = [str(s) for s in app._scope_requirements["flows.globus.org"]]
    assert len(str_list) == 2
    assert (
        "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/view_flows"
        in str_list
    )
    assert (
        "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run_status"
        in str_list
    )


def test_specific_flow_client_default_scopes():
    app = UserApp("test-app", client_id="client_id")
    globus_sdk.SpecificFlowClient("flow_id", app=app)

    assert [str(s) for s in app._scope_requirements["flow_id"]] == [
        "https://auth.globus.org/scopes/flow_id/flow_flow_id_user"
    ]
