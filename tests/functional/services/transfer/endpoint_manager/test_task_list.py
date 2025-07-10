import datetime
import uuid

import pytest

import globus_sdk
from globus_sdk.testing import get_last_request, load_response

ZERO_ID = uuid.UUID(int=0)


def get_last_params():
    return get_last_request().params


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
    load_response(client.endpoint_manager_task_list)
    paramstr = str(paramvalue)
    client.endpoint_manager_task_list(**{paramname: paramvalue})
    params = get_last_params()
    assert paramname in params
    assert params[paramname] == paramstr


def test_filter_status_list(client):
    load_response(client.endpoint_manager_task_list)
    client.endpoint_manager_task_list(filter_status=["ACTIVE", "INACTIVE"])
    params = get_last_params()
    assert "filter_status" in params
    assert params["filter_status"] == "ACTIVE,INACTIVE"


def test_filter_task_id_list(client):
    load_response(client.endpoint_manager_task_list)
    # mixed list of str and UUID
    client.endpoint_manager_task_list(filter_task_id=["foo", ZERO_ID, "bar"])
    params = get_last_params()
    assert "filter_task_id" in params
    assert params["filter_task_id"] == f"foo,{str(ZERO_ID)},bar"


def test_filter_completion_time_datetime_tuple(client):
    load_response(client.endpoint_manager_task_list)

    dt1 = datetime.datetime.fromisoformat("2020-08-25T00:00:00")
    dt2 = datetime.datetime.fromisoformat("2021-08-25T16:05:28")

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


@pytest.mark.parametrize("ep_use", ("source", "destination"))
def test_filter_by_endpoint_use(client, ep_use):
    meta = load_response(client.endpoint_manager_task_list).metadata
    if ep_use == "source":
        ep_id = meta["source"]
    else:
        ep_id = meta["destination"]

    client.endpoint_manager_task_list(filter_endpoint=ep_id, filter_endpoint_use=ep_use)
    params = get_last_params()

    assert "filter_endpoint" in params
    assert params["filter_endpoint"] == str(ep_id)
    assert "filter_endpoint_use" in params
    assert params["filter_endpoint_use"] == ep_use


@pytest.mark.parametrize("ep_use", ("source", "destination"))
def test_usage_error_on_filter_endpoint_use_without_endpoint(client, ep_use):
    with pytest.raises(
        globus_sdk.GlobusSDKUsageError,
        match=(
            "`filter_endpoint_use` is only valid when `filter_endpoint` is "
            r"also supplied\."
        ),
    ):
        client.endpoint_manager_task_list(filter_endpoint_use=ep_use)
