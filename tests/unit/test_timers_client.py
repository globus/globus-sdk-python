import pytest

import globus_sdk


def test_create_job_rejects_transfer_timer():
    client = globus_sdk.TimersClient()
    payload = globus_sdk.TransferTimer(schedule={"type": "once"}, body={})

    with pytest.raises(
        globus_sdk.GlobusSDKUsageError,
        match=r"Cannot pass a TransferTimer to create_job\(\)\.",
    ):
        client.create_job(payload)


def test_create_timer_rejects_timer_job():
    client = globus_sdk.TimersClient()
    payload = globus_sdk.TimerJob("https://bogus", {}, "2021-01-01T00:00:00Z", 300)

    with pytest.raises(
        globus_sdk.GlobusSDKUsageError,
        match=r"Cannot pass a TimerJob to create_timer\(\)\.",
    ):
        client.create_timer(payload)
