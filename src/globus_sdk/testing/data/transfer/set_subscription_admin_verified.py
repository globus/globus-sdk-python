import uuid

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import ENDPOINT_ID, SUBSCRIPTION_ID

NO_ADMIN_ROLE_ENDPOINT_ID = str(uuid.UUID(int=10))
NON_SUBSCRIBED_ENDPOINT_ID = str(uuid.UUID(int=11))
NO_IDENTITIES_IN_SESSION_ENDPOINT_ID = str(uuid.UUID(int=12))


def _format_verify_route(epid: str) -> str:
    return f"/endpoint/{epid}/subscription_admin_verified"


RESPONSES = ResponseSet(
    metadata={"endpoint_id": ENDPOINT_ID},
    default=RegisteredResponse(
        service="transfer",
        method="PUT",
        path=_format_verify_route(ENDPOINT_ID),
        status=200,
        json={
            "DATA_TYPE": "result",
            "code": "Updated",
            "message": "Endpoint updated successfully",
            "request_id": "SKWMqNWyv",
            "resource": _format_verify_route(ENDPOINT_ID),
        },
    ),
    no_admin_role=RegisteredResponse(
        metadata={"endpoint_id": NO_ADMIN_ROLE_ENDPOINT_ID},
        service="transfer",
        method="PUT",
        path=_format_verify_route(NO_ADMIN_ROLE_ENDPOINT_ID),
        status=403,
        json={
            "code": "PermissionDenied",
            "message": (
                "User does not have an admin role on the collection's "
                "subscription to set subscription_admin_verified"
            ),
            "request_id": "BHI2BHt8N",
            "resource": _format_verify_route(NO_ADMIN_ROLE_ENDPOINT_ID),
        },
    ),
    non_valid_verified_status=RegisteredResponse(
        service="transfer",
        method="PUT",
        path=_format_verify_route(ENDPOINT_ID),
        status=400,
        json={
            "code": "BadRequest",
            "message": (
                "Could not parse JSON: Expecting value: line 1 column 33 (char 32)"
            ),
            "request_id": "NPjnXpSD6",
            "resource": _format_verify_route(ENDPOINT_ID),
        },
    ),
    non_subscribed_endpoint=RegisteredResponse(
        metadata={"endpoint_id": NON_SUBSCRIBED_ENDPOINT_ID},
        service="transfer",
        method="PUT",
        path=_format_verify_route(NON_SUBSCRIBED_ENDPOINT_ID),
        status=400,
        json={
            "code": "BadRequest",
            "message": (
                "The collection must be associated with a subscription to "
                "set subscription_admin_verified"
            ),
            "request_id": "NPjnXpSD6",
            "resource": _format_verify_route(NON_SUBSCRIBED_ENDPOINT_ID),
        },
    ),
    no_identities_in_session=RegisteredResponse(
        metadata={
            "endpoint_id": NO_IDENTITIES_IN_SESSION_ENDPOINT_ID,
            "subscription_id": SUBSCRIPTION_ID,
        },
        service="transfer",
        method="PUT",
        path=_format_verify_route(NO_IDENTITIES_IN_SESSION_ENDPOINT_ID),
        status=400,
        json={
            "code": "BadRequest",
            "message": (
                "No manager or admin identities in session for high-assurance "
                f"subscription {SUBSCRIPTION_ID}"
            ),
            "request_id": "NPjnXpSD6",
            "resource": _format_verify_route(NO_IDENTITIES_IN_SESSION_ENDPOINT_ID),
        },
    ),
)
