import json

import globus_sdk
from globus_sdk._missing import filter_missing
from globus_sdk._testing import get_last_request, load_response


def test_dummy_timer_creation(client):
    # create a timer with a dummy payload and validate how it gets wrapped by the
    # sending method
    meta = load_response(client.create_timer).metadata

    timer = client.create_timer(timer={"foo": "bar"})
    assert timer["timer"]["job_id"] == meta["timer_id"]

    req = get_last_request()
    sent = json.loads(req.body)
    assert sent == {"timer": {"foo": "bar"}}


def test_transfer_timer_creation(client):
    # create a timer using the payload helpers and confirm that it is serialized as
    # desired
    meta = load_response(client.create_timer).metadata
    body = globus_sdk.TransferData(
        source_endpoint=meta["source_endpoint"],
        destination_endpoint=meta["destination_endpoint"],
    )
    body.add_item("/share/godata/file1.txt", "/~/file1.txt")

    schedule = globus_sdk.RecurringTimerSchedule(
        interval_seconds=60, end={"condition": "iterations", "iterations": 3}
    )

    timer = client.create_timer(
        timer=globus_sdk.TransferTimer(body=body, schedule=schedule)
    )
    assert timer["timer"]["job_id"] == meta["timer_id"]

    req = get_last_request()
    sent = json.loads(req.body)
    assert sent["timer"]["schedule"] == {
        "type": "recurring",
        "interval_seconds": 60,
        "end": {"condition": "iterations", "iterations": 3},
    }
    assert sent["timer"]["body"] == {
        k: [filter_missing(data_val) for data_val in v] if k == "DATA" else v
        for k, v in filter_missing(body).items()
        if k != "skip_activation_check"
    }
