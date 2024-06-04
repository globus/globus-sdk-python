from globus_sdk import TransferClient
from globus_sdk.experimental.globus_app import UserApp


def test_transfer_client_integration():
    rs = "transfer.api.globus.org"
    app = UserApp("test-app", client_id="client_id")
    client = TransferClient(app=app)

    assert [str(s) for s in app._scope_requirements[rs]] == [
        "urn:globus:auth:scope:transfer.api.globus.org:all"
    ]

    client.add_app_data_access_scope("collection_id")
    assert [str(s) for s in app._scope_requirements[rs]] == [
        "urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/collection_id/data_access]"  # noqa
    ]
