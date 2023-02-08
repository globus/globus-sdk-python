from __future__ import annotations

import typing as t

from globus_sdk._testing.models import RegisteredResponse, ResponseSet

raw_data: list[dict[str, t.Any]] = [
    {
        "name": "Claptrap's Rough Riders",
        "parent_id": None,
        "id": "d3974728-6458-11e4-b72d-123139141556",
        "group_type": "regular",
        "enforce_session": False,
        "session_limit": 28800,
        "session_timeouts": {},
        "my_memberships": [
            {
                "group_id": "d3974728-6458-11e4-b72d-123139141556",
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
    },
    {
        "name": "duke",
        "parent_id": "fdb38a24-03c1-11e3-86f7-12313809f035",
        "id": "7c580b9a-4592-11e3-a2a0-12313d2d6e7f",
        "group_type": "regular",
        "enforce_session": False,
        "session_limit": 28800,
        "session_timeouts": {},
        "my_memberships": [
            {
                "group_id": "7c580b9a-4592-11e3-a2a0-12313d2d6e7f",
                "identity_id": "ae332d86-d274-11e5-b885-b31714a110e9",
                "username": "sirosen@globusid.org",
                "role": "member",
                "status": "active",
            }
        ],
        "policies": {
            "group_visibility": "authenticated",
            "group_members_visibility": "members",
        },
    },
    {
        "name": "kbase_users",
        "parent_id": None,
        "id": "99d2a548-7218-11e2-adc0-12313d2d6e7f",
        "group_type": "regular",
        "enforce_session": False,
        "session_limit": 28800,
        "session_timeouts": {},
        "my_memberships": [
            {
                "group_id": "99d2a548-7218-11e2-adc0-12313d2d6e7f",
                "identity_id": "ae332d86-d274-11e5-b885-b31714a110e9",
                "username": "sirosen@globusid.org",
                "role": "member",
                "status": "active",
            }
        ],
        "policies": {
            "group_visibility": "authenticated",
            "group_members_visibility": "members",
        },
    },
    {
        "name": "connect",
        "parent_id": None,
        "id": "fdb38a24-03c1-11e3-86f7-12313809f035",
        "group_type": "regular",
        "enforce_session": False,
        "session_limit": 28800,
        "session_timeouts": {},
        "my_memberships": [
            {
                "group_id": "fdb38a24-03c1-11e3-86f7-12313809f035",
                "identity_id": "ae332d86-d274-11e5-b885-b31714a110e9",
                "username": "sirosen@globusid.org",
                "role": "member",
                "status": "active",
            }
        ],
        "policies": {
            "group_visibility": "authenticated",
            "group_members_visibility": "members",
        },
    },
    {
        "name": "sirosen's Email Testing Group",
        "parent_id": None,
        "id": "b0d168b0-6398-11e4-ac82-12313b077182",
        "group_type": "regular",
        "enforce_session": False,
        "session_limit": 28800,
        "session_timeouts": {},
        "my_memberships": [
            {
                "group_id": "b0d168b0-6398-11e4-ac82-12313b077182",
                "identity_id": "ae332d86-d274-11e5-b885-b31714a110e9",
                "username": "sirosen@globusid.org",
                "role": "admin",
                "status": "active",
            }
        ],
        "policies": {
            "group_visibility": "private",
            "group_members_visibility": "managers",
        },
    },
    {
        "name": "osg",
        "parent_id": "fdb38a24-03c1-11e3-86f7-12313809f035",
        "id": "80321e42-41a3-11e3-bef1-12313d2d6e7f",
        "group_type": "regular",
        "enforce_session": False,
        "session_limit": 28800,
        "session_timeouts": {},
        "my_memberships": [
            {
                "group_id": "80321e42-41a3-11e3-bef1-12313d2d6e7f",
                "identity_id": "ae332d86-d274-11e5-b885-b31714a110e9",
                "username": "sirosen@globusid.org",
                "role": "member",
                "status": "active",
            }
        ],
        "policies": {
            "group_visibility": "authenticated",
            "group_members_visibility": "members",
        },
    },
    {
        "name": "Search Examples: Cookery",
        "parent_id": None,
        "id": "0a4dea26-44cd-11e8-847f-0e6e723ad808",
        "group_type": "regular",
        "enforce_session": False,
        "session_limit": 28800,
        "session_timeouts": {},
        "my_memberships": [
            {
                "group_id": "0a4dea26-44cd-11e8-847f-0e6e723ad808",
                "identity_id": "ae341a98-d274-11e5-b888-dbae3a8ba545",
                "username": "sirosen@globus.org@accounts.google.com",
                "role": "admin",
                "status": "active",
            }
        ],
        "policies": {
            "group_visibility": "authenticated",
            "group_members_visibility": "managers",
        },
    },
]
group_ids = [x["id"] for x in raw_data]
group_names = [x["name"] for x in raw_data]
member_ids = {
    group["id"]: [m["identity_id"] for m in group["my_memberships"]]
    for group in raw_data
}

RESPONSES = ResponseSet(
    metadata={
        "group_ids": group_ids,
        "group_names": group_names,
        "member_ids": member_ids,
    },
    default=RegisteredResponse(
        service="groups",
        path="/groups/my_groups",
        json=raw_data,
    ),
)
