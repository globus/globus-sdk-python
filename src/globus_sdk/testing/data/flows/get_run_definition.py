import uuid

from globus_sdk._testing import RegisteredResponse, ResponseList, ResponseSet

from ._common import RUN_ID

GET_RUN_DEFINITION = {
    "flow_id": str(uuid.uuid4()),
    "definition": {
        "States": {"no-op": {"End": True, "Type": "Pass"}},
        "StartAt": "no-op",
    },
    "input_schema": {},
}


RESPONSES = ResponseSet(
    metadata={"run_id": RUN_ID},
    default=ResponseList(
        RegisteredResponse(
            service="flows",
            method="GET",
            path=f"/runs/{RUN_ID}/definition",
            json=GET_RUN_DEFINITION,
        ),
    ),
)
