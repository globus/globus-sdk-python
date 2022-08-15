import pytest

from globus_sdk import TimerJob, TransferData
from tests.common import GO_EP1_ID, GO_EP2_ID


def test_timer_from_transfer_data_ok():
    tdata = TransferData(None, GO_EP1_ID, GO_EP2_ID)
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
        TimerJob.from_transfer_data(tdata, "2022-01-01T00:00:00Z", 600)
