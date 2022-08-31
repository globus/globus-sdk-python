import json

from globus_sdk import UserCredentialDocument
from globus_sdk._testing import get_last_request, load_response


def test_get_user_credential_list(client):
    metadata = load_response(client.get_user_credential_list).metadata
    res = client.get_user_credential_list()

    assert len(list(res)) == 2
    # sanity check some fields
    assert res["DATA_TYPE"] == "result#1.0.0"
    for item in res:
        assert item["DATA_TYPE"] == "user_credential#1.0.0"
        assert item["id"] in metadata["ids"]
        assert "identity_id" in item
        assert "username" in item


def test_get_user_credential(client):
    metadata = load_response(client.get_user_credential).metadata
    uc_id = metadata["id"]
    res = client.get_user_credential(uc_id)

    assert res["DATA_TYPE"] == "user_credential#1.0.0"
    assert res.full_data["DATA_TYPE"] == "result#1.0.0"
    assert res["id"] == uc_id
    assert res["display_name"] == "posix_credential"
    assert client.connector_id_to_name(res["connector_id"]) == "POSIX"


def test_create_user_credential(client):
    metadata = load_response(client.create_user_credential).metadata
    uc_id = metadata["id"]

    data = UserCredentialDocument(
        storage_gateway_id="82247cc9-3208-4d71-bd7f-1b8798c95e6b",
        identity_id="948847d4-ffcc-4ae0-ba3a-a4c88d480159",
        username="testuser",
        display_name="s3_credential",
        policies={
            "DATA_TYPE": "s3_user_credential_policies#1.0.0",
            "s3_key_id": "foo",
            "s3_secret_key": "bar",
        },
    )

    res = client.create_user_credential(data)
    assert res["DATA_TYPE"] == "user_credential#1.0.0"
    assert res.full_data["DATA_TYPE"] == "result#1.0.0"
    assert res.full_data["message"] == f"Created User Credential {uc_id}"

    req_body = req_body = json.loads(get_last_request().body)
    assert req_body["DATA_TYPE"] == "user_credential#1.0.0"
    assert req_body["policies"]["DATA_TYPE"] == "s3_user_credential_policies#1.0.0"
    for key, value in req_body.items():
        assert data[key] == value


def test_update_user_credential(client):
    metadata = load_response(client.update_user_credential).metadata
    uc_id = metadata["id"]

    data = UserCredentialDocument(
        display_name="updated_posix_credential",
    )

    res = client.update_user_credential(uc_id, data)
    assert res["DATA_TYPE"] == "user_credential#1.0.0"
    assert res.full_data["DATA_TYPE"] == "result#1.0.0"
    assert res.full_data["message"] == f"Updated User Credential {uc_id}"

    req_body = json.loads(get_last_request().body)
    assert req_body["display_name"] == "updated_posix_credential"


def test_delete_user_credential(client):
    metadata = load_response(client.delete_user_credential).metadata
    uc_id = metadata["id"]

    res = client.delete_user_credential(uc_id)
    assert res["DATA_TYPE"] == "result#1.0.0"
    assert res["message"] == f"Deleted User Credential {uc_id}"
