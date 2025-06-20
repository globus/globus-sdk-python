"""
Tests for submitting Transfer and Delete tasks
"""

import json

import pytest

from globus_sdk import DeleteData, TransferAPIError, TransferData
from globus_sdk._testing import get_last_request, load_response
from tests.common import GO_EP1_ID, GO_EP2_ID


def test_transfer_submit_failure(client):
    load_response(client.get_submission_id)
    meta = load_response(client.submit_transfer, case="failure").metadata

    with pytest.raises(TransferAPIError) as excinfo:
        client.submit_transfer(TransferData(GO_EP1_ID, GO_EP2_ID))

    assert excinfo.value.http_status == 400
    assert excinfo.value.request_id == meta["request_id"]
    assert excinfo.value.code == "ClientError.BadRequest.NoTransferItems"


def test_transfer_submit_success(client):
    load_response(client.get_submission_id)
    meta = load_response(client.submit_transfer).metadata

    tdata = TransferData(
        GO_EP1_ID,
        GO_EP2_ID,
        label="mytask",
        sync_level="exists",
        deadline="2018-06-01",
        source_local_user="my-source-user",
        destination_local_user="my-dest-user",
        additional_fields={"custom_param": "foo"},
    )
    assert tdata["custom_param"] == "foo"
    assert tdata["sync_level"] == 0

    tdata.add_item("/path/to/foo", "/path/to/bar")
    tdata.add_symlink_item("linkfoo", "linkbar")

    res = client.submit_transfer(tdata)

    assert res
    assert res["submission_id"] == meta["submission_id"]
    assert res["task_id"] == meta["task_id"]

    req_body = json.loads(get_last_request().body)
    assert req_body["source_local_user"] == "my-source-user"
    assert req_body["destination_local_user"] == "my-dest-user"


def test_delete_submit_success(client):
    load_response(client.get_submission_id)
    meta = load_response(client.submit_delete).metadata

    ddata = DeleteData(
        endpoint=GO_EP1_ID,
        label="mytask",
        deadline="2018-06-01",
        local_user="my-user",
        additional_fields={"custom_param": "foo"},
    )
    assert ddata["custom_param"] == "foo"

    ddata.add_item("/path/to/foo")

    res = client.submit_delete(ddata)

    assert res
    assert res["submission_id"] == meta["submission_id"]
    assert res["task_id"] == meta["task_id"]

    req_body = json.loads(get_last_request().body)
    assert req_body["local_user"] == "my-user"


@pytest.mark.parametrize("datatype", ("transfer", "delete"))
def test_submit_adds_missing_submission_id_to_data(client, datatype):
    data = {}
    meta = load_response(client.get_submission_id).metadata
    if datatype == "transfer":
        load_response(client.submit_transfer)
        client.submit_transfer(data)
    else:
        load_response(client.submit_delete)
        client.submit_delete(data)
    assert "submission_id" in data
    assert data["submission_id"] == meta["submission_id"]
    req_body = json.loads(get_last_request().body)
    assert req_body == data


@pytest.mark.parametrize("datatype", ("transfer", "delete"))
def test_submit_does_not_overwrite_existing_submission_id(client, datatype):
    data = {"submission_id": "foo"}
    meta = load_response(client.get_submission_id).metadata
    if datatype == "transfer":
        load_response(client.submit_transfer)
        client.submit_transfer(data)
    else:
        load_response(client.submit_delete)
        client.submit_delete(data)
    assert data["submission_id"] == "foo"
    assert data["submission_id"] != meta["submission_id"]
    req_body = json.loads(get_last_request().body)
    assert req_body == data
