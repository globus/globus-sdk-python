from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TASK_ID

RESPONSES = ResponseSet(
    metadata={"task_id": TASK_ID},
    default=RegisteredResponse(
        service="transfer",
        method="GET",
        path=f"/endpoint_manager/task/{TASK_ID}/successful_transfers",
        json={
            "DATA_TYPE": "successful_transfers",
            "marker": 0,
            "next_marker": 93979,
            "DATA": [
                {
                    "destination_path": "/path/to/destination",
                    "source_path": "/path/to/source",
                    "DATA_TYPE": "successful_transfer",
                }
            ],
        },
    ),
)
