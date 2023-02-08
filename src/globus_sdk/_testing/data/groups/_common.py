from __future__ import annotations

import typing as t

GROUP_ID = "d3974728-6458-11e4-b72d-123139141556"

BASE_GROUP_DOC: dict[str, t.Any] = {
    "name": "Claptrap's Rough Riders",
    "description": "No stairs allowed.",
    "parent_id": None,
    "id": GROUP_ID,
    "group_type": "regular",
    "enforce_session": False,
    "session_limit": 28800,
    "session_timeouts": {},
    "my_memberships": [
        {
            "group_id": GROUP_ID,
            "identity_id": "ae332d86-d274-11e5-b885-b31714a110e9",
            "username": "sirosen@globusid.org",
            "role": "member",
            "status": "active",
        }
    ],
    "policies": {
        "group_visibility": "private",
        "group_members_visibility": "managers",
    },
}
