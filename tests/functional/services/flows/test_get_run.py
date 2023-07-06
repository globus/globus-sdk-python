import pytest

from globus_sdk._testing import get_last_request, load_response


@pytest.mark.parametrize("include_flow_description", (None, False, True))
def test_get_run(flows_client, include_flow_description):
    metadata = load_response(flows_client.get_run).metadata

    response = flows_client.get_run(
        metadata["run_id"],
        include_flow_description=include_flow_description,
    )
    assert response.http_status == 200

    request = get_last_request()
    if include_flow_description is None:
        assert "flow_description" not in response
        assert "include_flow_description" not in request.url
    elif include_flow_description is False:
        assert "flow_description" not in response
        assert "include_flow_description=False" in request.url
    else:  # include_flow_description is True
        assert "flow_description" in response
        assert "include_flow_description=True" in request.url
