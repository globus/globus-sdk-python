import uuid


def _as_uuid(s: str) -> str:
    return str(uuid.UUID(int=int(s, 36)))


SUBMISSION_ID = _as_uuid("submission_id")
ENDPOINT_ID = _as_uuid("endpoint_id")
TASK_ID = _as_uuid("task_id")
