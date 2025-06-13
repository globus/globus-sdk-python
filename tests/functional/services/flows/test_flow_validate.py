import json

import pytest

from globus_sdk import MISSING, FlowsAPIError
from globus_sdk._testing import get_last_request, load_response


@pytest.mark.parametrize("input_schema", [MISSING, {}])
def test_validate_flow(flows_client, input_schema):
    metadata = load_response(flows_client.validate_flow).metadata

    # Prepare the payload
    payload = {"definition": metadata["success"]}
    if input_schema is not MISSING:
        payload["input_schema"] = input_schema

    resp = flows_client.validate_flow(**payload)
    assert resp.data["scopes"] == {
        "User": ["urn:globus:auth:scope:transfer.api.globus.org:all"]
    }

    # Check what was actually sent
    last_req = get_last_request()
    req_body = json.loads(last_req.body)
    # Ensure the input schema is not sent if omitted
    assert req_body == payload


def test_validate_flow_error_parsing(flows_client):
    metadata = load_response(
        flows_client.validate_flow, case="definition_error"
    ).metadata

    # Make sure we get an error response
    with pytest.raises(FlowsAPIError) as excinfo:
        flows_client.validate_flow(definition=metadata["invalid"])

    err = excinfo.value
    assert err.code == "UNPROCESSABLE_ENTITY"
    assert err.messages == [
        (
            "A state of type 'Action' must be defined as either terminal "
            '("End": true) or transitional ("Next": "NextStateId")'
        ),
    ]
