from globus_sdk.testing import load_response


def test_get_clients(service_client):
    meta = load_response(service_client.get_clients).metadata
    res = service_client.get_clients()

    assert {client["id"] for client in res["clients"]} == set(meta["client_ids"])
