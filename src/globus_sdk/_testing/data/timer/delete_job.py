from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .get_job import JOB_ID, JOB_JSON

RESPONSES = ResponseSet(
    metadata={"job_id": JOB_ID},
    default=RegisteredResponse(
        service="timer",
        path=f"/jobs/{JOB_ID}",
        method="DELETE",
        json=JOB_JSON,
    ),
)
