from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .get_job import JOB_ID

RESPONSES = ResponseSet(
    metadata={"job_id": JOB_ID},
    default=RegisteredResponse(
        service="timer",
        path=f"/jobs/{JOB_ID}/pause",
        method="POST",
        json={"message": f"Successfully paused job {JOB_ID}."},
    ),
)
