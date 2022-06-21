from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .get_job import JOB_ID, JOB_JSON

RESPONSES = ResponseSet(
    metadata={"job_ids": [JOB_ID]},
    default=RegisteredResponse(
        service="timer",
        path="/jobs/",
        method="GET",
        json={"jobs": [JOB_JSON]},
    ),
)
