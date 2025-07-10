import datetime
import json

import pytest

from globus_sdk import TimerJob, TimersAPIError, TransferData, config, exc
from globus_sdk._utils import slash_join
from globus_sdk.testing import get_last_request, load_response
from tests.common import GO_EP1_ID, GO_EP2_ID


def test_list_jobs(client):
    meta = load_response(client.list_jobs).metadata
    response = client.list_jobs()
    assert response.http_status == 200
    assert set(meta["job_ids"]) == {job["job_id"] for job in response.data["jobs"]}


def test_get_job(client):
    meta = load_response(client.get_job).metadata
    response = client.get_job(meta["job_id"])
    assert response.http_status == 200
    assert response.data.get("job_id") == meta["job_id"]


def test_get_job_errors(client):
    meta = load_response(client.get_job, case="simple_500_error").metadata
    with pytest.raises(TimersAPIError) as excinfo:
        client.get_job(meta["job_id"])
    err = excinfo.value
    assert err.http_status == 500
    assert err.code == "ERROR"
    assert err.message == "Request failed terribly"


@pytest.mark.parametrize("start", [datetime.datetime.now(), "2022-04-05T06:00:00"])
@pytest.mark.parametrize(
    "interval", [datetime.timedelta(days=1), datetime.timedelta(minutes=60), 600, None]
)
def test_create_job(client, start, interval):
    meta = load_response(client.create_job).metadata
    transfer_data = TransferData(GO_EP1_ID, GO_EP2_ID)
    with pytest.warns(exc.RemovedInV4Warning, match="Prefer TransferTimer"):
        timer_job = TimerJob.from_transfer_data(transfer_data, start, interval)
    response = client.create_job(timer_job)
    assert response.http_status == 201
    assert response.data["job_id"] == meta["job_id"]
    with pytest.warns(exc.RemovedInV4Warning, match="Prefer TransferTimer"):
        timer_job = TimerJob.from_transfer_data(dict(transfer_data), start, interval)
    response = client.create_job(timer_job)
    assert response.http_status == 201
    assert response.data["job_id"] == meta["job_id"]
    req_body = json.loads(get_last_request().body)
    if isinstance(start, datetime.datetime):
        assert req_body["start"] == start.isoformat()
    else:
        assert req_body["start"] == start
    if isinstance(interval, datetime.timedelta):
        assert req_body["interval"] == interval.total_seconds()
    else:
        assert req_body["interval"] == interval
    assert req_body["callback_url"] == slash_join(
        config.get_service_url("actions"), "/transfer/transfer/run"
    )


def test_create_job_validation_error(client):
    meta = load_response(client.create_job, case="validation_error").metadata
    transfer_data = TransferData(GO_EP1_ID, GO_EP2_ID)
    with pytest.warns(exc.RemovedInV4Warning, match="Prefer TransferTimer"):
        timer_job = TimerJob.from_transfer_data(
            transfer_data, "2022-04-05T06:00:00", 1800
        )

    with pytest.raises(TimersAPIError) as excinfo:
        client.create_job(timer_job)

    err = excinfo.value
    assert err.http_status == 422
    assert err.code is None
    assert err.messages == meta["expect_messages"]


def test_update_job(client):
    meta = load_response(client.update_job).metadata
    response = client.update_job(meta["job_id"], {"name": meta["name"]})
    assert response.http_status == 200
    assert response.data["job_id"] == meta["job_id"]
    assert response.data["name"] == meta["name"]


def test_delete_job(client):
    meta = load_response(client.delete_job).metadata
    response = client.delete_job(meta["job_id"])
    assert response.http_status == 200
    assert response.data["job_id"] == meta["job_id"]


def test_pause_job(client):
    meta = load_response(client.pause_job).metadata
    response = client.pause_job(meta["job_id"])
    assert response.http_status == 200
    assert "Successfully paused" in response.data["message"]


@pytest.mark.parametrize("update_credentials", [True, False, None])
def test_resume_job(update_credentials, client):
    meta = load_response(client.resume_job).metadata

    kwargs = {}
    if update_credentials is not None:
        kwargs["update_credentials"] = update_credentials

    response = client.resume_job(meta["job_id"], **kwargs)
    assert response.http_status == 200
    assert json.loads(response._raw_response.request.body) == kwargs
    assert "Successfully resumed" in response.data["message"]
