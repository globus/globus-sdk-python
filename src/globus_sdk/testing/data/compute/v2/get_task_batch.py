from responses.matchers import json_params_matcher

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .._common import TASK_DOC, TASK_ID

TASK_BATCH_DOC = {
    "response": "batch",
    "results": {TASK_ID: TASK_DOC},
}

RESPONSES = ResponseSet(
    metadata={"task_id": TASK_ID},
    default=RegisteredResponse(
        service="compute",
        path="/v2/batch_status",
        method="POST",
        json=TASK_BATCH_DOC,
        # Ensure task_ids is a list
        match=[json_params_matcher({"task_ids": [TASK_ID]})],
    ),
)
