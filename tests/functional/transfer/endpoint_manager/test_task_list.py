import datetime
import uuid

import pytest

from globus_sdk._testing import get_last_request
from tests.common import register_api_route

ZERO_ID = uuid.UUID(int=0)


def get_last_params():
    return get_last_request().params


# stub in empty data, this can be explicitly replaced if a test wants specific data
@pytest.fixture(autouse=True)
def empty_response():
    register_api_route("transfer", "/endpoint_manager/task_list", json={"DATA": []})


@pytest.mark.parametrize(
    "paramname, paramvalue",
    [
        ("filter_task_id", ZERO_ID),
        ("filter_task_id", "foo"),
        ("filter_owner_id", ZERO_ID),
        ("filter_owner_id", "foo"),
        ("filter_endpoint", ZERO_ID),
        ("filter_endpoint", "foo"),
        ("filter_is_paused", True),
        ("filter_is_paused", False),
        ("filter_min_faults", 0),
        ("filter_min_faults", 10),
        ("filter_local_user", "foouser"),
        ("filter_status", "ACTIVE"),
        ("filter_completion_time", "2020-08-25T00:00:00,2021-08-25T16:05:28"),
    ],
)
def test_strsafe_params(client, paramname, paramvalue):
    paramstr = str(paramvalue)
    client.endpoint_manager_task_list(**{paramname: paramvalue})
    params = get_last_params()
    assert paramname in params
    assert params[paramname] == paramstr


def test_filter_status_list(client):
    client.endpoint_manager_task_list(filter_status=["ACTIVE", "INACTIVE"])
    params = get_last_params()
    assert "filter_status" in params
    assert params["filter_status"] == "ACTIVE,INACTIVE"


def test_filter_task_id_list(client):
    # mixed list of str and UUID
    client.endpoint_manager_task_list(filter_task_id=["foo", ZERO_ID, "bar"])
    params = get_last_params()
    assert "filter_task_id" in params
    assert params["filter_task_id"] == f"foo,{str(ZERO_ID)},bar"


def _fromisoformat(datestr):  # for py3.6, datetime.fromisoformat was added in py3.7
    return datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S")


def test_filter_completion_time_datetime_tuple(client):
    dt1 = _fromisoformat("2020-08-25T00:00:00")
    dt2 = _fromisoformat("2021-08-25T16:05:28")

    client.endpoint_manager_task_list(filter_completion_time=(dt1, dt2))
    params = get_last_params()
    assert "filter_completion_time" in params
    assert params["filter_completion_time"] == "2020-08-25T00:00:00,2021-08-25T16:05:28"

    # mixed tuples work, important for passing `""`
    client.endpoint_manager_task_list(filter_completion_time=(dt1, ""))
    params = get_last_params()
    assert "filter_completion_time" in params
    assert params["filter_completion_time"] == "2020-08-25T00:00:00,"
    client.endpoint_manager_task_list(filter_completion_time=("", dt1))
    params = get_last_params()
    assert "filter_completion_time" in params
    assert params["filter_completion_time"] == ",2020-08-25T00:00:00"
