from globus_sdk._testing.models import RegisteredResponse, ResponseSet

from ._common import TWO_HOP_TRANSFER_FLOW_DOC, TWO_HOP_TRANSFER_FLOW_ID

_DELETED_DOC = {
    "DELETED": True,
    "administered_by": [],
    "api_version": "1.0",
    "created_at": TWO_HOP_TRANSFER_FLOW_DOC["created_at"],
    "created_by": TWO_HOP_TRANSFER_FLOW_DOC["created_by"],
    "definition": TWO_HOP_TRANSFER_FLOW_DOC["definition"],
    "deleted_at": "2022-10-20T16:44:59.126641+00:00",
    "description": "",
    "flow_administrators": [],
    "flow_owner": TWO_HOP_TRANSFER_FLOW_DOC["flow_owner"],
    "flow_starters": [],
    "flow_viewers": [],
    "globus_auth_scope": TWO_HOP_TRANSFER_FLOW_DOC["globus_auth_scope"],
    "globus_auth_username": TWO_HOP_TRANSFER_FLOW_DOC["globus_auth_username"],
    "id": TWO_HOP_TRANSFER_FLOW_ID,
    "input_schema": {},
    "keywords": [],
    "log_supported": True,
    "principal_urn": TWO_HOP_TRANSFER_FLOW_DOC["principal_urn"],
    "runnable_by": [],
    "subtitle": "",
    "synchronous": False,
    "title": TWO_HOP_TRANSFER_FLOW_DOC["title"],
    "types": ["Action"],
    "updated_at": "2022-10-20T16:44:59.021201+00:00",
    "user_role": "flow_owner",
    "visible_to": [],
}

RESPONSES = ResponseSet(
    metadata={"flow_id": TWO_HOP_TRANSFER_FLOW_ID},
    default=RegisteredResponse(
        service="flows",
        path=f"/flows/{TWO_HOP_TRANSFER_FLOW_ID}",
        method="DELETE",
        json=_DELETED_DOC,
    ),
)
