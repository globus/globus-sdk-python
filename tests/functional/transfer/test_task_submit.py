"""
Tests for submitting Transfer and Delete tasks
"""
import pytest

import globus_sdk
from globus_sdk._testing import load_response
from tests.common import GO_EP1_ID, GO_EP2_ID


@pytest.fixture
def transfer_data(client):
    load_response(client.get_submission_id)

    def _transfer_data(**kwargs):
        return globus_sdk.TransferData(client, GO_EP1_ID, GO_EP2_ID, **kwargs)

    return _transfer_data


@pytest.fixture
def delete_data(client):
    load_response(client.get_submission_id)

    def _delete_data(**kwargs):
        return globus_sdk.DeleteData(client, GO_EP1_ID, **kwargs)

    return _delete_data


def test_transfer_submit_failure(client, transfer_data):
    meta = load_response(client.submit_transfer, case="failure").metadata

    with pytest.raises(globus_sdk.TransferAPIError) as excinfo:
        client.submit_transfer(transfer_data())

    assert excinfo.value.http_status == 400
    assert excinfo.value.request_id == meta["request_id"]
    assert excinfo.value.code == "ClientError.BadRequest.NoTransferItems"


def test_transfer_submit_success(client, transfer_data):
    meta = load_response(client.submit_transfer).metadata

    tdata = transfer_data(
        label="mytask",
        sync_level="exists",
        deadline="2018-06-01",
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


def test_delete_submit_success(client, delete_data):
    meta = load_response(client.submit_delete).metadata

    ddata = delete_data(
        label="mytask", deadline="2018-06-01", additional_fields={"custom_param": "foo"}
    )
    assert ddata["custom_param"] == "foo"

    ddata.add_item("/path/to/foo")

    res = client.submit_delete(ddata)

    assert res
    assert res["submission_id"] == meta["submission_id"]
    assert res["task_id"] == meta["task_id"]
