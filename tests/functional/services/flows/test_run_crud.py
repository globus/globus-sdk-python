import json

import pytest

from globus_sdk import FlowsAPIError
from globus_sdk.testing import get_last_request, load_response


def test_get_run_definition(flows_client):
    """Validate the HTTP method and route used to get the flow definition for a run."""

    run_id = load_response(flows_client.get_run_definition).metadata["run_id"]

    flows_client.get_run_definition(run_id)
    request = get_last_request()
    assert request.method == "GET"
    assert request.url.endswith(f"/runs/{run_id}/definition")


def test_cancel_run(flows_client):
    """Verify that run cancellation requests meet expectations."""

    run_id = load_response(flows_client.cancel_run).metadata["run_id"]

    flows_client.cancel_run(run_id)
    request = get_last_request()
    assert request.method == "POST"
    assert request.url.endswith(f"/runs/{run_id}/cancel")


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


def test_delete_run_success(flows_client):
    """Verify `.delete_run()` requests match expectations."""

    metadata = load_response(flows_client.delete_run).metadata
    flows_client.delete_run(metadata["run_id"])

    request = get_last_request()
    assert request.method == "POST"
    assert request.url.endswith(f"/runs/{metadata['run_id']}/release")
    # Ensure no deprecated routes are used.
    assert "/flows/" not in request.url


def test_delete_run_conflict(flows_client):
    """Verify the `.delete_run()` HTTP 409 CONFLICT test case matches expectations."""

    metadata = load_response(flows_client.delete_run, case="conflict").metadata

    with pytest.raises(FlowsAPIError) as error:
        flows_client.delete_run(metadata["run_id"])

    assert error.value.http_status == 409
