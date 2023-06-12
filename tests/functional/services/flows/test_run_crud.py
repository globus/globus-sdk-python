import json

import pytest

from globus_sdk._testing import get_last_request, load_response


@pytest.mark.parametrize(
    "values",
    (
        {},
        {"label": "x"},
        {"run_monitors": []},
        {"run_monitors": ["me", "you"]},
        {"run_managers": []},
        {"run_managers": ["me", "you"]},
        {"tags": []},
        {"tags": ["x"]},
    ),
)
def test_update_run(flows_client, values):
    metadata = load_response(flows_client.update_run).metadata

    flows_client.update_run(metadata["run_id"], **values)
    request = get_last_request()
    assert request.method == "PUT"
    assert request.url.endswith(f"/runs/{metadata['run_id']}")
    assert json.loads(request.body) == values

    # Ensure deprecated routes are not used.
    assert f"/flows/{metadata['flow_id']}" not in request.url


def test_update_run_additional_fields(flows_client):
    """*addition_fields* must override all other parameters."""

    metadata = load_response(flows_client.update_run).metadata

    additional_fields = {
        "label": "x",
        "run_monitors": ["x"],
        "run_managers": ["x"],
        "tags": ["x"],
    }

    flows_client.update_run(
        metadata["run_id"],
        label="a",
        run_managers=["a"],
        run_monitors=["a"],
        tags=["a"],
        additional_fields=additional_fields,
    )
    request = get_last_request()
    assert request.method == "PUT"
    assert request.url.endswith(f"/runs/{metadata['run_id']}")
    assert json.loads(request.body) == additional_fields
