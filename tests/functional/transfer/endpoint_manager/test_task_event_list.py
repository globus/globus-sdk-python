import uuid

import pytest

from globus_sdk._testing import get_last_request
from tests.common import register_api_route

ZERO_ID = uuid.UUID(int=0)


def get_last_params():
    return get_last_request().params


@pytest.fixture
def task_id():
    return uuid.uuid1()


# stub in empty data, this can be explicitly replaced if a test wants specific data
@pytest.fixture(autouse=True)
def empty_response(task_id):
    register_api_route(
        "transfer", f"/endpoint_manager/task/{task_id}/event_list", json={"DATA": []}
    )


# although int values are not supported based on the type annotations, users may already
# be passing ints -- it's good to support this usage and test it even if it's not
# documented and desirable
@pytest.mark.parametrize(
    "paramvalue, paramstr", [(True, "1"), (False, "0"), (1, "1"), (0, "0")]
)
def test_filter_is_error(client, task_id, paramvalue, paramstr):
    client.endpoint_manager_task_event_list(task_id, filter_is_error=paramvalue)
    params = get_last_params()
    assert "filter_is_error" in params
    assert params["filter_is_error"] == paramstr
