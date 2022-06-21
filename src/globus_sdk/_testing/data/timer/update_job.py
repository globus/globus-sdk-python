from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from .get_job import JOB_ID, JOB_JSON

UPDATED_NAME = "updated name"
UPDATED_JSON = dict(JOB_JSON)
UPDATED_JSON["name"] = UPDATED_NAME  # mypy complains if this is onelinerized

RESPONSES = ResponseSet(
    metadata={"job_id": JOB_ID, "name": UPDATED_NAME},
    default=RegisteredResponse(
        service="timer",
        path=f"/jobs/{JOB_ID}",
        method="PATCH",
        json=UPDATED_JSON,
    ),
)
