from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TIMER_ID, V1_TIMER

TIMER_INACTIVE_USER = {
    **V1_TIMER,
    "status": "inactive",
    "inactive_reason": {"cause": "user", "detail": None},
}

TIMER_INACTIVE_GARE = {
    **V1_TIMER,
    "status": "inactive",
    "inactive_reason": {
        "cause": "globus_auth_requirements",
        "detail": {
            "code": "ConsentRequired",
            "authorization_parameters": {
                "session_message": "Missing required data_access consent",
                "required_scopes": [
                    (
                        "https://auth.globus.org/scopes/actions.globus.org/"
                        "transfer/transfer"
                        "[urn:globus:auth:scope:transfer.api.globus.org:all"
                        "[*https://auth.globus.org/scopes/"
                        "543aade1-db97-4a4b-9bdf-0b58e78dfa69/data_access]]"
                    )
                ],
            },
        },
    },
}


RESPONSES = ResponseSet(
    metadata={"job_id": TIMER_ID},
    default=RegisteredResponse(
        service="timer",
        path=f"/jobs/{TIMER_ID}",
        method="GET",
        json=V1_TIMER,
    ),
    inactive_gare=RegisteredResponse(
        service="timer",
        path=f"/jobs/{TIMER_ID}",
        method="GET",
        json=TIMER_INACTIVE_GARE,
    ),
    inactive_user=RegisteredResponse(
        service="timer",
        path=f"/jobs/{TIMER_ID}",
        method="GET",
        json=TIMER_INACTIVE_USER,
    ),
    simple_500_error=RegisteredResponse(
        service="timer",
        path=f"/jobs/{TIMER_ID}",
        method="GET",
        status=500,
        json={
            "error": {
                "code": "ERROR",
                "detail": "Request failed terribly",
                "status": 500,
            }
        },
    ),
)
