from globus_sdk.testing import load_response


def test_get_policies(service_client):
    meta = load_response(service_client.get_policies).metadata
    res = service_client.get_policies()

    assert {policy["id"] for policy in res["policies"]} == set(meta["policy_ids"])
