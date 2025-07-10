import typing as t
import uuid

import pytest

import globus_sdk
from globus_sdk.testing import load_response


@pytest.mark.parametrize(
    "transform",
    (
        pytest.param(lambda x: x, id="string"),
        pytest.param(lambda x: [x], id="list"),
        pytest.param(lambda x: {x}, id="set"),
        pytest.param(lambda x: uuid.UUID(x), id="uuid"),
        pytest.param(lambda x: [uuid.UUID(x)], id="uuid_list"),
    ),
)
def test_get_task_batch(
    compute_client_v2: globus_sdk.ComputeClientV2, transform: t.Callable
):
    meta = load_response(compute_client_v2.get_task_batch).metadata
    task_ids = transform(meta["task_id"])
    res = compute_client_v2.get_task_batch(task_ids=task_ids)

    assert res.http_status == 200
    assert meta["task_id"] in res.data["results"]
