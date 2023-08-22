from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .get_job import JOB_ID

RESPONSES = ResponseSet(
    metadata={"job_id": JOB_ID},
    default=RegisteredResponse(
        service="timer",
        path=f"/jobs/{JOB_ID}/resume",
        method="POST",
        json={"message": f"Successfully resumed job {JOB_ID}."},
    ),
)
