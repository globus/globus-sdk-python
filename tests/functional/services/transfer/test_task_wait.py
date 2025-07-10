from unittest import mock

import pytest
import responses

import globus_sdk
from globus_sdk.testing import get_last_request
from tests.common import register_api_route_fixture_file

TASK1_ID = "b8872740-7edc-11ec-9f33-ed182a728dff"


@pytest.mark.parametrize(
    "add_kwargs",
    [
        {"timeout": 0, "polling_interval": 0},
        {"timeout": 0.5, "polling_interval": 0.5},
        {"timeout": 5, "polling_interval": 0.5},
        {"timeout": -5, "polling_interval": 5},
    ],
)
def test_task_wait_bad_args_min_wait(client, mocksleep, add_kwargs):
    # register task mock data even though it should not be needed
    register_api_route_fixture_file(
        "transfer", f"/task/{TASK1_ID}", "get_task1_active.json"
    )

    with pytest.raises(globus_sdk.GlobusSDKUsageError):
        client.task_wait(TASK1_ID, **add_kwargs)

    # no requests sent, no sleep done
    assert get_last_request() is None
    mocksleep.assert_not_called()


def test_task_wait_success_case(client, mocksleep):
    # first the task will show as active, then as succeeded
    register_api_route_fixture_file(
        "transfer", f"/task/{TASK1_ID}", "get_task1_active.json"
    )
    register_api_route_fixture_file(
        "transfer", f"/task/{TASK1_ID}", "get_task1_succeeded.json"
    )

    # do the task wait, it should return true (the task completed in time)
    result = client.task_wait(TASK1_ID, timeout=5, polling_interval=1)
    assert result is True

    # one sleep, two network calls
    mocksleep.assert_called_once_with(1)
    assert len(responses.calls) == 2


def test_task_wait_unfinished_case(client, mocksleep):
    # the task is in the active state no matter how many times we ask
    register_api_route_fixture_file(
        "transfer", f"/task/{TASK1_ID}", "get_task1_active.json"
    )

    # do the task wait, it should return false (the task didn't complete)
    result = client.task_wait(TASK1_ID, timeout=5, polling_interval=1)
    assert result is False

    # a number of sleeps equal to timeout/polling_interval
    # a number of requests equal to sleeps+1
    mocksleep.assert_has_calls([mock.call(1) for x in range(5)])
    assert len(responses.calls) == 6
