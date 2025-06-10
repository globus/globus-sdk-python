import datetime

import pytest

from globus_sdk import (
    OnceTimerSchedule,
    RecurringTimerSchedule,
    TimerJob,
    TransferData,
    TransferTimer,
    exc,
)
from globus_sdk._missing import filter_missing
from tests.common import GO_EP1_ID, GO_EP2_ID


def test_timer_from_transfer_data_ok():
    tdata = TransferData(None, GO_EP1_ID, GO_EP2_ID)
    with pytest.warns(exc.RemovedInV4Warning, match="Prefer TransferTimer"):
        job = TimerJob.from_transfer_data(tdata, "2022-01-01T00:00:00Z", 600)
    assert "callback_body" in job
    assert "body" in job["callback_body"]
    assert "source_endpoint" in job["callback_body"]["body"]
    assert "destination_endpoint" in job["callback_body"]["body"]
    assert job["callback_body"]["body"]["source_endpoint"] == GO_EP1_ID
    assert job["callback_body"]["body"]["destination_endpoint"] == GO_EP2_ID


@pytest.mark.parametrize(
    "badkey, value", (("submission_id", "foo"), ("skip_activation_check", True))
)
def test_timer_from_transfer_data_rejects_forbidden_keys(badkey, value):
    tdata = TransferData(None, GO_EP1_ID, GO_EP2_ID, **{badkey: value})
    with pytest.raises(ValueError):
        with pytest.warns(exc.RemovedInV4Warning, match="Prefer TransferTimer"):
            TimerJob.from_transfer_data(tdata, "2022-01-01T00:00:00Z", 600)


def test_transfer_timer_ok():
    tdata = TransferData(source_endpoint=GO_EP1_ID, destination_endpoint=GO_EP2_ID)
    timer = TransferTimer(body=tdata, name="foo timer", schedule={"type": "once"})
    assert timer["name"] == "foo timer"
    assert timer["schedule"]["type"] == "once"
    assert {"source_endpoint", "destination_endpoint"} < timer["body"].keys()
    assert timer["body"]["source_endpoint"] == GO_EP1_ID
    assert timer["body"]["destination_endpoint"] == GO_EP2_ID


def test_transfer_timer_removes_disallowed_fields():
    # set transfer-data-like body with disallowed fields
    tdata = {"submission_id": "foo", "skip_activation_check": False, "foo": "bar"}
    timer = TransferTimer(body=tdata, name="foo timer", schedule={"type": "once"})
    assert timer["name"] == "foo timer"
    assert timer["schedule"]["type"] == "once"

    # confirm that disallowed fields are stripped in the timer,
    # but the original dict is unchanged
    assert timer["body"] == {"foo": "bar"}
    assert set(tdata.keys()) == {"submission_id", "skip_activation_check", "foo"}


@pytest.mark.parametrize(
    "input_time, expected",
    (
        # even though this string is "obviously" not a valid datetime, we don't
        # translate it when we create the schedule
        ("tomorrow", "tomorrow"),
        # use a fixed (known) timestamp and check how it's formatted as UTC
        (datetime.datetime.fromtimestamp(1698385129.7044), "2023-10-27T05:38:49+00:00"),
        # use a non-UTC datetime and confirm that it is sent as non-UTC
        (
            datetime.datetime.fromisoformat("2023-10-27T05:38:49.999+01:00"),
            "2023-10-27T05:38:49+01:00",
        ),
    ),
)
def test_once_timer_schedule_formats_datetime(input_time, expected):
    schedule = OnceTimerSchedule(datetime=input_time)
    assert schedule.data == {"type": "once", "datetime": expected}


def test_recurring_timer_schedule_interval_only():
    schedule = RecurringTimerSchedule(interval_seconds=600)
    assert filter_missing(schedule) == {
        "type": "recurring",
        "interval_seconds": 600,
    }


@pytest.mark.parametrize(
    "input_time, expected",
    (
        # even though this string is "obviously" not a valid datetime, we don't
        # translate it when we create the schedule
        ("tomorrow", "tomorrow"),
        # use a fixed (known) timestamp and check how it's formatted
        (datetime.datetime.fromtimestamp(1698385129.7044), "2023-10-27T05:38:49+00:00"),
    ),
)
def test_recurring_timer_schedule_formats_start(input_time, expected):
    schedule = RecurringTimerSchedule(interval_seconds=600, start=input_time)
    assert filter_missing(schedule) == {
        "type": "recurring",
        "interval_seconds": 600,
        "start": expected,
    }


def test_recurring_timer_schedule_formats_datetime_for_end():
    # use a fixed (known) timestamp and check how it's formatted
    end_time = datetime.datetime.fromtimestamp(1698385129.7044)
    schedule = RecurringTimerSchedule(
        interval_seconds=600, end={"condition": "time", "datetime": end_time}
    )
    assert filter_missing(schedule) == {
        "type": "recurring",
        "interval_seconds": 600,
        "end": {"condition": "time", "datetime": "2023-10-27T05:38:49+00:00"},
    }
